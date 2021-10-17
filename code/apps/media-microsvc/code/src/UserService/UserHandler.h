#ifndef MEDIA_MICROSERVICES_USERHANDLER_H
#define MEDIA_MICROSERVICES_USERHANDLER_H

#include <iostream>
#include <string>
#include <random>
#include <mongoc.h>
#include <bson/bson.h>
#include <libmemcached/memcached.h>
#include <libmemcached/util.h>
#include <iomanip>
#include <arpa/inet.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <nlohmann/json.hpp>
#include <jwt/jwt.hpp>

#include "../tracing.h"
#include "../../gen-cpp/UserService.h"
#include "../../gen-cpp/media_service_types.h"
#include "../ClientPool.h"
#include "../ThriftClient.h"
#include "../../gen-cpp/ComposeReviewService.h"
#include "../../third_party/PicoSHA2/picosha2.h"
#include "../logger.h"

// Custom Epoch (January 1, 2018 Midnight GMT = 2018-01-01T00:00:00Z)
#define CUSTOM_EPOCH 1514764800000

namespace media_service {

using std::chrono::milliseconds;
using std::chrono::duration_cast;
using std::chrono::system_clock;
//using namespace jwt::params;

static int64_t current_timestamp = -1;
static int counter = 0;

static int GetCounter(int64_t timestamp) {
  if (current_timestamp > timestamp) {
    LOG(fatal) << "Timestamps are not incremental.";
    exit(EXIT_FAILURE);
  }
  if (current_timestamp == timestamp) {
    return counter++;
  } else {
    current_timestamp = timestamp;
    counter = 0;
    return counter++;
  }
}

std::string GenRandomString(const int len) {
  static const std::string alphanum =
      "0123456789"
      "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
      "abcdefghijklmnopqrstuvwxyz";
  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<int> dist(
      0, static_cast<int>(alphanum.length() - 1));
  std::string s;
  for (int i = 0; i < len; ++i) {
    s += alphanum[dist(gen)];
  }
  return s;
}

class UserHandler : public UserServiceIf {
 public:
  UserHandler(
      std::mutex*,
      const std::string &,
      const std::string &,
      memcached_pool_st *,
      mongoc_client_pool_t *,
      ClientPool<ThriftClient<ComposeReviewServiceClient>> *);
  ~UserHandler() override = default;
  void RegisterUser(
      int64_t,
      const std::string &,
      const std::string &,
      const std::string &,
      const std::string &,
      const std::map<std::string, std::string> &) override;
  void RegisterUserWithId(int64_t req_id, const std::string& first_name,
      const std::string& last_name, const std::string& username,
      const std::string& password, int64_t user_id,
      const std::map<std::string, std::string> & carrier) override;
  void UploadUserWithUserId(
      int64_t,
      int64_t,
      const std::map<std::string, std::string> &) override;
  void UploadUserWithUsername(
      int64_t,
      const std::string &,
      const std::map<std::string, std::string> &) override;
  void Login(
      std::string &,
      int64_t,
      const std::string &,
      const std::string &,
      const std::map<std::string, std::string> &) override;
 private:
  std::string _machine_id;
  std::string _secret;
  std::mutex *_thread_lock;
  memcached_pool_st *_memcached_client_pool;
  mongoc_client_pool_t *_mongodb_client_pool;
  ClientPool<ThriftClient<ComposeReviewServiceClient>> *_compose_client_pool;

};

UserHandler::UserHandler(
    std::mutex *thread_lock,
    const std::string &machine_id,
    const std::string &secret,
    memcached_pool_st *memcached_client_pool,
    mongoc_client_pool_t *mongodb_client_pool,
    ClientPool<ThriftClient<ComposeReviewServiceClient>> *compose_client_pool
    ) {
  _thread_lock = thread_lock;
  _machine_id = machine_id;
  _memcached_client_pool = memcached_client_pool;
  _mongodb_client_pool = mongodb_client_pool;
  _compose_client_pool = compose_client_pool;
  _secret = secret;
}

void UserHandler::RegisterUser(
    const int64_t req_id,
    const std::string &first_name,
    const std::string &last_name,
    const std::string &username,
    const std::string &password,
    const std::map<std::string, std::string> &carrier) {
  
  LOG(warning) << "start";
  auto start = std::chrono::high_resolution_clock::now();
  auto timetaken_by_external_calls = 0;

  // Initialize a span
  // TextMapReader reader(carrier);
  std::map<std::string, std::string> writer_text_map;
  // TextMapWriter writer(writer_text_map);
  // auto parent_span = opentracing::Tracer::Global()->Extract(reader);
  auto span = opentracing::Tracer::Global()->StartSpan("RegisterUser");

  // Compose user_id
  int64_t timestamp = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count() - CUSTOM_EPOCH;
  std::stringstream sstream;
  sstream << std::hex << timestamp;
  std::string timestamp_hex(sstream.str());
  if (timestamp_hex.size() > 10) {
    timestamp_hex.erase(0, timestamp_hex.size() - 10);
  } else if (timestamp_hex.size() < 10) {
    timestamp_hex =
        std::string(10 - timestamp_hex.size(), '0') + timestamp_hex;
  }
  _thread_lock->lock();
  int counter = GetCounter(timestamp);
  _thread_lock->unlock();
  // Empty the sstream buffer.
  sstream.clear();
  sstream.str(std::string());

  sstream << std::hex << counter;
  std::string counter_hex(sstream.str());

  if (counter_hex.size() > 3) {
    counter_hex.erase(0, counter_hex.size() - 3);
  } else if (counter_hex.size() < 3) {
    counter_hex = std::string(3 - counter_hex.size(), '0') + counter_hex;
  }
  std::string user_id_str = _machine_id + timestamp_hex + counter_hex;
  int64_t user_id = stoul(user_id_str, nullptr, 16) & 0x7FFFFFFFFFFFFFFF;
  LOG(debug) << "The user_id of the request " << req_id << " is " << user_id;

  auto started_mongo_find = std::chrono::high_resolution_clock::now();
  mongoc_client_t *mongodb_client = mongoc_client_pool_pop(_mongodb_client_pool);
  auto timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
  timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;

  if (!mongodb_client) {
    ServiceException se;
    se.errorCode = ErrorCode::SE_MONGODB_ERROR;
    se.message = "Failed to pop a client from MongoDB pool";
    throw se;
  }
  
  started_mongo_find = std::chrono::high_resolution_clock::now(); 
  auto collection = mongoc_client_get_collection(mongodb_client, "user", "user");
  timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
  timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;

  // Check if the username has existed in the database
  bson_t *query = bson_new();
  BSON_APPEND_UTF8(query, "username", username.c_str());
  
  started_mongo_find = std::chrono::high_resolution_clock::now(); 
  mongoc_cursor_t *cursor = mongoc_collection_find_with_opts(collection, query, nullptr, nullptr);
  timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
  timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
 
  const bson_t *doc;
  started_mongo_find = std::chrono::high_resolution_clock::now(); 
  if (mongoc_cursor_next(cursor, &doc)) {
    timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
    timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
    bson_error_t error;
    if (mongoc_cursor_error (cursor, &error)) {
      LOG(warning) << error.message;
      bson_destroy(query);
      mongoc_cursor_destroy(cursor);
      mongoc_collection_destroy(collection);
      mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
      ServiceException se;
      se.errorCode = ErrorCode::SE_MONGODB_ERROR;
      se.message = error.message;
      throw se;
    } else {
      timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
      timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
      LOG(warning) << "User " << username << " already existed.";
      ServiceException se;
      se.errorCode = ErrorCode::SE_THRIFT_HANDLER_ERROR;
      se.message = "User " + username + " already existed";
      bson_destroy(query);
      mongoc_cursor_destroy(cursor);
      mongoc_collection_destroy(collection);
      mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
      throw se;
    }
  } else {
    bson_t *new_doc = bson_new();
    BSON_APPEND_INT64(new_doc, "user_id", user_id);
    BSON_APPEND_UTF8(new_doc, "first_name", first_name.c_str());
    BSON_APPEND_UTF8(new_doc, "last_name", last_name.c_str());
    BSON_APPEND_UTF8(new_doc, "username", username.c_str());
    std::string salt = GenRandomString(32);
    BSON_APPEND_UTF8(new_doc, "salt", salt.c_str());
    std::string password_hashed = picosha2::hash256_hex_string(password + salt);
    BSON_APPEND_UTF8(new_doc, "password", password_hashed.c_str());

    bson_error_t error;
    started_mongo_find = std::chrono::high_resolution_clock::now(); 
    if (!mongoc_collection_insert_one(
        collection, new_doc, nullptr, nullptr, &error)) {
      
      timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
      timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
      LOG(error) << "Failed to insert user " << username
          << " to MongoDB: " << error.message;
      ServiceException se;
      se.errorCode = ErrorCode::SE_THRIFT_HANDLER_ERROR;
      se.message = "Failed to insert user " + username + " to MongoDB: "
          + error.message;
      bson_destroy(query);
      mongoc_cursor_destroy(cursor);
      mongoc_collection_destroy(collection);
      mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
      throw se;
    } else {
      timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
      timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
      LOG(debug) << "User: " << username << " registered";
    }
    bson_destroy(new_doc);
  }
  mongoc_cursor_destroy(cursor);
  mongoc_collection_destroy(collection);
  mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);

  double timetaken = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-start).count();
  LOG(warning) << timetaken-timetaken_by_external_calls; 
  span->Log({{"runtime_ms",timetaken-timetaken_by_external_calls}});
  span->Finish();
  LOG(warning) << "end";
}

void UserHandler::RegisterUserWithId(
    int64_t req_id, const std::string& first_name,
    const std::string& last_name, const std::string& username,
    const std::string& password, int64_t user_id,
    const std::map<std::string, std::string> & carrier) {

  LOG(warning) << "start";
  auto start = std::chrono::high_resolution_clock::now();
  auto timetaken_by_external_calls = 0;

  // Initialize a span
  // TextMapReader reader(carrier);
  std::map<std::string, std::string> writer_text_map;
  // TextMapWriter writer(writer_text_map);
  // auto parent_span = opentracing::Tracer::Global()->Extract(reader);
  auto span = opentracing::Tracer::Global()->StartSpan("RegisterUserWithId");

  auto started_mongo_find = std::chrono::high_resolution_clock::now();
  mongoc_client_t *mongodb_client = mongoc_client_pool_pop(_mongodb_client_pool);
  auto timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
  timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;

  if (!mongodb_client) {
    ServiceException se;
    se.errorCode = ErrorCode::SE_MONGODB_ERROR;
    se.message = "Failed to pop a client from MongoDB pool";
    throw se;
  }
  
  started_mongo_find = std::chrono::high_resolution_clock::now(); 
  auto collection = mongoc_client_get_collection(mongodb_client, "user", "user");
  timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
  timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;

  // Check if the username has existed in the database
  bson_t *query = bson_new();
  BSON_APPEND_UTF8(query, "username", username.c_str());
  
  started_mongo_find = std::chrono::high_resolution_clock::now();  
  mongoc_cursor_t *cursor = mongoc_collection_find_with_opts(collection, query, nullptr, nullptr);
  timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
  timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
 
  const bson_t *doc;
  
  started_mongo_find = std::chrono::high_resolution_clock::now(); 
  if (mongoc_cursor_next(cursor, &doc)) {
    timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
    timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
    bson_error_t error;
    if (mongoc_cursor_error (cursor, &error)) {
      LOG(warning) << error.message;
      bson_destroy(query);
      mongoc_cursor_destroy(cursor);
      mongoc_collection_destroy(collection);
      mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
      ServiceException se;
      se.errorCode = ErrorCode::SE_MONGODB_ERROR;
      se.message = error.message;
      throw se;
    } else {
      timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
      timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
      LOG(warning) << "User " << username << " already existed.";
      ServiceException se;
      se.errorCode = ErrorCode::SE_THRIFT_HANDLER_ERROR;
      se.message = "User " + username + " already existed";
      bson_destroy(query);
      mongoc_cursor_destroy(cursor);
      mongoc_collection_destroy(collection);
      mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
      throw se;
    }
  } else {
    bson_t *new_doc = bson_new();
    BSON_APPEND_INT64(new_doc, "user_id", user_id);
    BSON_APPEND_UTF8(new_doc, "first_name", first_name.c_str());
    BSON_APPEND_UTF8(new_doc, "last_name", last_name.c_str());
    BSON_APPEND_UTF8(new_doc, "username", username.c_str());
    std::string salt = GenRandomString(32);
    BSON_APPEND_UTF8(new_doc, "salt", salt.c_str());
    std::string password_hashed = picosha2::hash256_hex_string(password + salt);
    BSON_APPEND_UTF8(new_doc, "password", password_hashed.c_str());

    bson_error_t error;
    
    started_mongo_find = std::chrono::high_resolution_clock::now(); 
    if (!mongoc_collection_insert_one(collection, new_doc, nullptr, nullptr, &error)) {
      
      timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
      timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
      LOG(error) << "Failed to insert user " << username
                 << " to MongoDB: " << error.message;
      ServiceException se;
      se.errorCode = ErrorCode::SE_THRIFT_HANDLER_ERROR;
      se.message = "Failed to insert user " + username + " to MongoDB: "
          + error.message;
      bson_destroy(query);
      mongoc_cursor_destroy(cursor);
      mongoc_collection_destroy(collection);
      mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
      throw se;
    } else {
      LOG(debug) << "User: " << username << " registered";
    }
    bson_destroy(new_doc);
  }
  mongoc_cursor_destroy(cursor);
  mongoc_collection_destroy(collection);
  mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);

  double timetaken = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-start).count();
  LOG(warning) << timetaken-timetaken_by_external_calls; 
  span->Log({{"runtime_ms",timetaken-timetaken_by_external_calls}});
  span->Finish();
  LOG(warning) << "end";
}

void UserHandler::UploadUserWithUsername(const int64_t req_id, const std::string &username, const std::map<std::string, std::string> & carrier) {

  LOG(warning) << "start";
  auto start = std::chrono::high_resolution_clock::now();
  auto timetaken_by_external_calls = 0;

  // TextMapReader reader(carrier);
  std::map<std::string, std::string> writer_text_map;
  // TextMapWriter writer(writer_text_map);
  auto span = opentracing::Tracer::Global()->StartSpan("UploadUserWithUsername");
    

  size_t user_id_size;
  uint32_t memcached_flags;
  memcached_return_t memcached_rc;
  auto started_mongo_find = std::chrono::high_resolution_clock::now();
  memcached_st *memcached_client = memcached_pool_pop(_memcached_client_pool, true, &memcached_rc);
  auto timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
  timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;

  if (!memcached_client) {
    ServiceException se;
    se.errorCode = ErrorCode::SE_MEMCACHED_ERROR;
    se.message = "Failed to pop a client from memcached pool";
    throw se;
  }

  started_mongo_find = std::chrono::high_resolution_clock::now();
  char *user_id_mmc = memcached_get(memcached_client, (username+":user_id").c_str(), (username+":user_id").length(), &user_id_size, &memcached_flags, &memcached_rc);
  timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
  timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
  if (!user_id_mmc && memcached_rc != MEMCACHED_NOTFOUND) {
    ServiceException se;
    se.errorCode = ErrorCode::SE_MEMCACHED_ERROR;
    se.message = memcached_strerror(memcached_client, memcached_rc);
    memcached_pool_push(_memcached_client_pool, memcached_client);
    throw se;
  }
  memcached_pool_push(_memcached_client_pool, memcached_client);

  int64_t user_id = 0;

  if (user_id_mmc) {
    LOG(debug) << "Found password, salt and ID are cached in Memcached";
    user_id = std::stoul(user_id_mmc);
  }

  // If not cached in memcached
  else {
    LOG(debug) << "User_id not cached in Memcached";
    
    started_mongo_find = std::chrono::high_resolution_clock::now();
    mongoc_client_t *mongodb_client = mongoc_client_pool_pop(_mongodb_client_pool);
    timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
    timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
    
    if (!mongodb_client) {
      ServiceException se;
      se.errorCode = ErrorCode::SE_MONGODB_ERROR;
      se.message = "Failed to pop a client from MongoDB pool";
      free(user_id_mmc);
      throw se;
    }
    started_mongo_find = std::chrono::high_resolution_clock::now(); 
    auto collection = mongoc_client_get_collection(mongodb_client, "user", "user");
    timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
    timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
    
    if (!collection) {
      ServiceException se;
      se.errorCode = ErrorCode::SE_MONGODB_ERROR;
      se.message = "Failed to create collection user from DB user";
      free(user_id_mmc);
      throw se;
    }
    bson_t *query = bson_new();
    BSON_APPEND_UTF8(query, "username", username.c_str());

    started_mongo_find = std::chrono::high_resolution_clock::now(); 
    mongoc_cursor_t *cursor = mongoc_collection_find_with_opts(collection, query, nullptr, nullptr);
    const bson_t *doc;
    bool found = mongoc_cursor_next(cursor, &doc);
    timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
    timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
    
    if (!found) {
      bson_error_t error;
      if (mongoc_cursor_error (cursor, &error)) {
        LOG(warning) << error.message;
        mongoc_collection_destroy(collection);
        mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
        ServiceException se;
        se.errorCode = ErrorCode::SE_MONGODB_ERROR;
        se.message = error.message;
        free(user_id_mmc);
        throw se;
      } else {
        LOG(warning) << "User: " << username << " doesn't exist in MongoDB";
        mongoc_collection_destroy(collection);
        mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
        ServiceException se;
        se.errorCode = ErrorCode::SE_THRIFT_HANDLER_ERROR;
        se.message = "User: " + username + " is not registered";
        free(user_id_mmc);
        throw se;
      }
    } else {
      LOG(debug) << "User: " << username << " found in MongoDB";
      bson_iter_t iter;
      if (bson_iter_init_find(&iter, doc, "user_id")) {
        user_id = bson_iter_value(&iter)->value.v_int64;
      } else {
        LOG(error) << "user_id attribute of user " << username <<" was not found in the User object";
        bson_destroy(query);
        mongoc_cursor_destroy(cursor);
        mongoc_collection_destroy(collection);
        mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
        ServiceException se;
        se.errorCode = ErrorCode::SE_THRIFT_HANDLER_ERROR;
        se.message = "user_id attribute of user: " + username +" was not found in the User object";
        free(user_id_mmc);
        throw se;
      }
    }
    bson_destroy(query);
    mongoc_cursor_destroy(cursor);
    mongoc_collection_destroy(collection);
    mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
  }

  if (user_id) {
    started_mongo_find = std::chrono::high_resolution_clock::now();
    auto compose_client_wrapper = _compose_client_pool->Pop();
    timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
    timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
    if (!compose_client_wrapper) {
      ServiceException se;
      se.errorCode = ErrorCode::SE_THRIFT_CONN_ERROR;
      se.message = "Failed to connected to compose-review-service";
      throw se;
    }
    auto compose_client = compose_client_wrapper->GetClient();
    try {
      started_mongo_find = std::chrono::high_resolution_clock::now();
      compose_client->UploadUserId(req_id, user_id, writer_text_map);
      timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
      timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
    } catch (...) {
      //_compose_client_pool->Push(compose_client_wrapper);
      LOG(error) << "Failed to upload movie_id to compose-review-service";
      throw;
    }
    _compose_client_pool->Push(compose_client_wrapper);
  }
  
  started_mongo_find = std::chrono::high_resolution_clock::now();
  memcached_client = memcached_pool_pop(_memcached_client_pool, true, &memcached_rc);
  timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
  timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;

  if (!memcached_client) {
    ServiceException se;
    se.errorCode = ErrorCode::SE_MEMCACHED_ERROR;
    se.message = "Failed to pop a client from memcached pool";
    free(user_id_mmc);
    throw se;
  }

  if (user_id && !user_id_mmc) {
  
    std::string user_id_str = std::to_string(user_id);
    started_mongo_find = std::chrono::high_resolution_clock::now();
    memcached_rc = memcached_set(
        memcached_client,
        (username+":user_id").c_str(),
        (username+":user_id").length(),
        user_id_str.c_str(),
        user_id_str.length(),
        static_cast<time_t>(0),
        static_cast<uint32_t>(0)
    );
    timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
    timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;

    if (memcached_rc != MEMCACHED_SUCCESS) {
      LOG(warning)
        << "Failed to set the user_id of user "
        << username << " to Memcached: "
        << memcached_strerror(memcached_client, memcached_rc);
    }
  }
  memcached_pool_push(_memcached_client_pool, memcached_client);

  free(user_id_mmc);
  double timetaken = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-start).count();
  LOG(warning) << timetaken-timetaken_by_external_calls; 
  span->Log({{"runtime_ms",timetaken-timetaken_by_external_calls}});
  span->Finish();
  LOG(warning) << "end";
}

void UserHandler::UploadUserWithUserId(
    int64_t req_id,
    int64_t user_id,
    const std::map<std::string, std::string> &carrier) {


  LOG(warning) << "start";
  auto start = std::chrono::high_resolution_clock::now();
  auto timetaken_by_external_calls = 0;

  std::map<std::string, std::string> writer_text_map;
  auto span = opentracing::Tracer::Global()->StartSpan("UploadUserWithUserId");

  auto started_mongo_find = std::chrono::high_resolution_clock::now();
  auto compose_client_wrapper = _compose_client_pool->Pop();
  auto timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
  timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;

  if (!compose_client_wrapper) {
    ServiceException se;
    se.errorCode = ErrorCode::SE_THRIFT_CONN_ERROR;
    se.message = "Failed to connected to compose-review-service";
    throw se;
  }
  auto compose_client = compose_client_wrapper->GetClient();
  try {
    started_mongo_find = std::chrono::high_resolution_clock::now();
    compose_client->UploadUserId(req_id, user_id, writer_text_map);
    timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
    timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call; 
  } catch (...) {
    //_compose_client_pool->Push(compose_client_wrapper);
    LOG(error) << "Failed to upload movie_id to compose-review-service";
    throw;
  }
  _compose_client_pool->Push(compose_client_wrapper);

  double timetaken = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-start).count();
  LOG(warning) << timetaken-timetaken_by_external_calls; 
  span->Log({{"runtime_ms",timetaken-timetaken_by_external_calls}});
  span->Finish();
  LOG(warning) << "end";
}


void UserHandler::Login(
    std::string & _return,
    int64_t req_id,
    const std::string &username,
    const std::string &password,
    const std::map<std::string, std::string> &carrier) {

  LOG(warning) << "start";
  auto start = std::chrono::high_resolution_clock::now();
  auto timetaken_by_external_calls = 0;

  std::map<std::string, std::string> writer_text_map;
  auto span = opentracing::Tracer::Global()->StartSpan("Login");

  size_t password_size;
  size_t salt_size;
  size_t user_id_size;
  uint32_t memcached_flags;

  memcached_return_t memcached_rc;
  
  auto started_mongo_find = std::chrono::high_resolution_clock::now();
  memcached_st *memcached_client = memcached_pool_pop(_memcached_client_pool, true, &memcached_rc);
  auto timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
  timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;

  if (!memcached_client) {
    ServiceException se;
    se.errorCode = ErrorCode::SE_MEMCACHED_ERROR;
    se.message = "Failed to pop a client from memcached pool";
    throw se;
  }

  started_mongo_find = std::chrono::high_resolution_clock::now();
  char *password_mmc = memcached_get(
      memcached_client,
      (username+":password").c_str(),
      (username+":password").length(),
      &password_size,
      &memcached_flags,
      &memcached_rc);
  timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
  timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;

   if (!password_mmc && memcached_rc != MEMCACHED_NOTFOUND) {
    ServiceException se;
    se.errorCode = ErrorCode::SE_MEMCACHED_ERROR;
    se.message = memcached_strerror(memcached_client, memcached_rc);
    memcached_pool_push(_memcached_client_pool, memcached_client);
    throw se;
  }

  started_mongo_find = std::chrono::high_resolution_clock::now();
  char *salt_mmc = memcached_get(
      memcached_client,
      (username+":salt").c_str(),
      (username+":salt").length(),
      &salt_size,
      &memcached_flags,
      &memcached_rc);
  timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
  timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
 
  if (!salt_mmc && memcached_rc != MEMCACHED_NOTFOUND) {
    ServiceException se;
    se.errorCode = ErrorCode::SE_MEMCACHED_ERROR;
    se.message = memcached_strerror(memcached_client, memcached_rc);
    memcached_pool_push(_memcached_client_pool, memcached_client);
    free(password_mmc);
    throw se;
  }


  started_mongo_find = std::chrono::high_resolution_clock::now();
  char *user_id_mmc = memcached_get(
      memcached_client,
      (username+":user_id").c_str(),
      (username+":user_id").length(),
      &user_id_size,
      &memcached_flags,
      &memcached_rc);
  timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
  timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
 
  if (!user_id_mmc && memcached_rc != MEMCACHED_NOTFOUND) {
    ServiceException se;
    se.errorCode = ErrorCode::SE_MEMCACHED_ERROR;
    se.message = memcached_strerror(memcached_client, memcached_rc);
    memcached_pool_push(_memcached_client_pool, memcached_client);
    free(salt_mmc);
    free(password_mmc);
    throw se;
  }

  memcached_pool_push(_memcached_client_pool, memcached_client);

  int64_t user_id = 0;
  const char *salt_str = nullptr;
  const char *password_str = nullptr;

  if (password_mmc && salt_mmc && user_id_mmc) {
    LOG(debug) << "Found password, salt and ID are cached in Memcached";
    user_id = std::stoul(user_id_mmc);
    password_str = password_mmc;
    salt_str = salt_mmc;
  }

    // If not cached in memcached
  else {
    LOG(debug) << "Password or salt or ID not cached in Memcached";
    
    started_mongo_find = std::chrono::high_resolution_clock::now();
    mongoc_client_t *mongodb_client = mongoc_client_pool_pop(_mongodb_client_pool);
    timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
    timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
 
    if (!mongodb_client) {
      ServiceException se;
      se.errorCode = ErrorCode::SE_MONGODB_ERROR;
      se.message = "Failed to pop a client from MongoDB pool";
      free(salt_mmc);
      free(password_mmc);
      free(user_id_mmc);
      throw se;
    }
    
    started_mongo_find = std::chrono::high_resolution_clock::now(); 
    auto collection = mongoc_client_get_collection(mongodb_client, "user", "user");
    timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
    timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
 
    if (!collection) {
      ServiceException se;
      se.errorCode = ErrorCode::SE_MONGODB_ERROR;
      se.message = "Failed to create collection user from DB user";
      free(salt_mmc);
      free(password_mmc);
      free(user_id_mmc);
      throw se;
    }
    bson_t *query = bson_new();
    BSON_APPEND_UTF8(query, "username", username.c_str());

    started_mongo_find = std::chrono::high_resolution_clock::now(); 
    mongoc_cursor_t *cursor = mongoc_collection_find_with_opts(collection, query, nullptr, nullptr);
    const bson_t *doc;
    bool found = mongoc_cursor_next(cursor, &doc);
    timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
    timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
 
    if (!found) {
      bson_error_t error;
      if (mongoc_cursor_error (cursor, &error)) {
        LOG(warning) << error.message;
        mongoc_collection_destroy(collection);
        mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
        ServiceException se;
        se.errorCode = ErrorCode::SE_MONGODB_ERROR;
        se.message = error.message;
        free(salt_mmc);
        free(password_mmc);
        free(user_id_mmc);
        throw se;
      } else {
        LOG(warning) << "User: " << username << " doesn't exist in MongoDB";
        mongoc_collection_destroy(collection);
        mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
        ServiceException se;
        se.errorCode = ErrorCode::SE_UNAUTHORIZED;
        se.message = "User: " + username + " is not registered";
        free(salt_mmc);
        free(password_mmc);
        free(user_id_mmc);
        throw se;
      }
    } else {
      LOG(debug) << "User: " << username << " found in MongoDB";
      if (!password_mmc) {
        bson_iter_t iter;
        if (bson_iter_init_find(&iter, doc, "password")) {
          password_str = bson_iter_value(&iter)->value.v_utf8.str;
        } else {
          LOG(error) << "Password attribute of user "
                     << username <<" was not found in the User object";
          bson_destroy(query);
          mongoc_cursor_destroy(cursor);
          mongoc_collection_destroy(collection);
          mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
          ServiceException se;
          se.errorCode = ErrorCode::SE_THRIFT_HANDLER_ERROR;
          se.message = "Password attribute of user: " + username +
              " was not found in the User object";
          free(salt_mmc);
          free(password_mmc);
          free(user_id_mmc);
          throw se;
        }
      }

      if (!salt_mmc) {
        bson_iter_t iter;
        if (bson_iter_init_find(&iter, doc, "salt")) {
          salt_str = bson_iter_value(&iter)->value.v_utf8.str;
        } else {
          LOG(error) << "Salt attribute of user "
                     << username <<" was not found in the User object";
          bson_destroy(query);
          mongoc_cursor_destroy(cursor);
          mongoc_collection_destroy(collection);
          mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
          ServiceException se;
          se.errorCode = ErrorCode::SE_THRIFT_HANDLER_ERROR;
          se.message = "Salt attribute of user: " + username +
              " was not found in the User object";
          free(salt_mmc);
          free(password_mmc);
          free(user_id_mmc);
          throw se;
        }
      }

      if (!user_id_mmc) {
        bson_iter_t iter;
        if (bson_iter_init_find(&iter, doc, "user_id")) {
          user_id = bson_iter_value(&iter)->value.v_int64;
        } else {
          LOG(error) << "user_Id attribute of user "
                     << username <<" was not found in the User object";
          bson_destroy(query);
          mongoc_cursor_destroy(cursor);
          mongoc_collection_destroy(collection);
          mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
          ServiceException se;
          se.errorCode = ErrorCode::SE_THRIFT_HANDLER_ERROR;
          se.message = "User_id attribute of user: " + username +
              " was not found in the User object";
          free(salt_mmc);
          free(password_mmc);
          free(user_id_mmc);
          throw se;
        }
      }
    }

    bson_destroy(query);
    mongoc_cursor_destroy(cursor);
    mongoc_collection_destroy(collection);
    mongoc_client_pool_push(_mongodb_client_pool, mongodb_client);
  }

  if (user_id && salt_str && password_str) {
    bool auth = picosha2::hash256_hex_string(password + std::string(salt_str))
        == std::string(password_str);
    if (auth) {
      auto user_id_str = std::to_string(user_id);
      auto timestamp_str = std::to_string(duration_cast<milliseconds>(
          system_clock::now().time_since_epoch()).count());


      jwt::jwt_object obj{
          jwt::params::algorithm("HS256"),
          jwt::params::secret(_secret),
          jwt::params::payload({
              {"user_id", user_id_str},
              {"timestamp", timestamp_str},
              {"TTL", "60000"}
          })
      };
      _return = obj.signature();

    } else {
      ServiceException se;
      se.errorCode = ErrorCode::SE_UNAUTHORIZED;
      se.message = "Incorrect username or password";
      free(salt_mmc);
      free(password_mmc);
      free(user_id_mmc);
      throw se;
    }
  }

  started_mongo_find = std::chrono::high_resolution_clock::now();
  memcached_client = memcached_pool_pop(_memcached_client_pool, true, &memcached_rc);
  timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
  timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;

  if (!memcached_client) {
    ServiceException se;
    se.errorCode = ErrorCode::SE_MEMCACHED_ERROR;
    se.message = "Failed to pop a client from memcached pool";
    free(salt_mmc);
    free(password_mmc);
    free(user_id_mmc);
    throw se;
  }

  if (salt_str && !salt_mmc) {

    started_mongo_find = std::chrono::high_resolution_clock::now();
    memcached_rc = memcached_set(
        memcached_client,
        (username+":salt").c_str(),
        (username+":salt").length(),
        salt_str,
        std::strlen(salt_str),
        0,
        0
    );
    timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
    timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;

    if (memcached_rc != MEMCACHED_SUCCESS) {
      LOG(warning)
        << "Failed to set the salt of user "
        << username << " to Memcached: "
        << memcached_strerror(memcached_client, memcached_rc);
    }
  }

  if (password_str && !password_mmc) {

    started_mongo_find = std::chrono::high_resolution_clock::now();
    memcached_rc = memcached_set(
        memcached_client,
        (username+":password").c_str(),
        (username+":password").length(),
        password_str,
        std::strlen(password_str),
        static_cast<time_t>(0),
        static_cast<uint32_t>(0)
    );
    timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
    timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;

    if (memcached_rc != MEMCACHED_SUCCESS) {
      LOG(warning)
        << "Failed to set the password of user "
        << username << " to Memcached: "
        << memcached_strerror(memcached_client, memcached_rc);
    }
  }

  if (user_id && !user_id_mmc) {
    
    started_mongo_find = std::chrono::high_resolution_clock::now();
    std::string user_id_str = std::to_string(user_id);
    memcached_rc = memcached_set(
        memcached_client,
        (username+":user_id").c_str(),
        (username+":user_id").length(),
        user_id_str.c_str(),
        user_id_str.length(),
        static_cast<time_t>(0),
        static_cast<uint32_t>(0)
    );
    timetaken_mongo_call = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-started_mongo_find).count();
    timetaken_by_external_calls = timetaken_by_external_calls + timetaken_mongo_call;
    if (memcached_rc != MEMCACHED_SUCCESS) {
      LOG(warning)
        << "Failed to set the user_id of user "
        << username << " to Memcached: "
        << memcached_strerror(memcached_client, memcached_rc);
    }
  }
  memcached_pool_push(_memcached_client_pool, memcached_client);

  free(salt_mmc);
  free(password_mmc);
  free(user_id_mmc);
  auto timetaken = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now()-start).count();
  span->Log({{"runtime_ms",timetaken-timetaken_by_external_calls}});
  span->Finish();
  LOG(warning) << "end";
}

/*
 * The following code which obtaines machine ID from machine's MAC address was
 * inspired from https://stackoverflow.com/a/16859693.
 */
u_int16_t HashMacAddressPid(const std::string &mac)
{
  u_int16_t hash = 0;
  std::string mac_pid = mac + std::to_string(getpid());
  for ( unsigned int i = 0; i < mac_pid.size(); i++ ) {
    hash += ( mac[i] << (( i & 1 ) * 8 ));
  }
  return hash;
}

int GetMachineId (std::string *mac_hash) {
  std::string mac;
  int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP );
  if ( sock < 0 ) {
    LOG(error) << "Unable to obtain MAC address";
    return -1;
  }

  struct ifconf conf{};
  char ifconfbuf[ 128 * sizeof(struct ifreq)  ];
  memset( ifconfbuf, 0, sizeof( ifconfbuf ));
  conf.ifc_buf = ifconfbuf;
  conf.ifc_len = sizeof( ifconfbuf );
  if ( ioctl( sock, SIOCGIFCONF, &conf ))
  {
    LOG(error) << "Unable to obtain MAC address";
    return -1;
  }

  struct ifreq* ifr;
  for (
      ifr = conf.ifc_req;
      reinterpret_cast<char *>(ifr) <
          reinterpret_cast<char *>(conf.ifc_req) + conf.ifc_len;
      ifr++) {
    if ( ifr->ifr_addr.sa_data == (ifr+1)->ifr_addr.sa_data ) {
      continue;  // duplicate, skip it
    }

    if ( ioctl( sock, SIOCGIFFLAGS, ifr )) {
      continue;  // failed to get flags, skip it
    }
    if ( ioctl( sock, SIOCGIFHWADDR, ifr ) == 0 ) {
      mac = std::string(ifr->ifr_addr.sa_data);
      if (!mac.empty()) {
        break;
      }
    }
  }
  close(sock);

  std::stringstream stream;
  stream << std::hex << HashMacAddressPid(mac);
  *mac_hash = stream.str();

  if (mac_hash->size() > 3) {
    mac_hash->erase(0, mac_hash->size() - 3);
  } else if (mac_hash->size() < 3) {
    *mac_hash = std::string(3 - mac_hash->size(), '0') + *mac_hash;
  }
  return 0;
}
} // namespace media_service

#endif //MEDIA_MICROSERVICES_USERHANDLER_H




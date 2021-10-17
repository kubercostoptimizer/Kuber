/**
 * Autogenerated by Thrift Compiler (0.12.0)
 *
 * DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
 *  @generated
 */
#include "RatingService.h"

namespace media_service {


RatingService_UploadRating_args::~RatingService_UploadRating_args() throw() {
}


uint32_t RatingService_UploadRating_args::read(::apache::thrift::protocol::TProtocol* iprot) {

  ::apache::thrift::protocol::TInputRecursionTracker tracker(*iprot);
  uint32_t xfer = 0;
  std::string fname;
  ::apache::thrift::protocol::TType ftype;
  int16_t fid;

  xfer += iprot->readStructBegin(fname);

  using ::apache::thrift::protocol::TProtocolException;


  while (true)
  {
    xfer += iprot->readFieldBegin(fname, ftype, fid);
    if (ftype == ::apache::thrift::protocol::T_STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
        if (ftype == ::apache::thrift::protocol::T_I64) {
          xfer += iprot->readI64(this->req_id);
          this->__isset.req_id = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 2:
        if (ftype == ::apache::thrift::protocol::T_STRING) {
          xfer += iprot->readString(this->movie_id);
          this->__isset.movie_id = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 3:
        if (ftype == ::apache::thrift::protocol::T_I32) {
          xfer += iprot->readI32(this->rating);
          this->__isset.rating = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 4:
        if (ftype == ::apache::thrift::protocol::T_MAP) {
          {
            this->carrier.clear();
            uint32_t _size87;
            ::apache::thrift::protocol::TType _ktype88;
            ::apache::thrift::protocol::TType _vtype89;
            xfer += iprot->readMapBegin(_ktype88, _vtype89, _size87);
            uint32_t _i91;
            for (_i91 = 0; _i91 < _size87; ++_i91)
            {
              std::string _key92;
              xfer += iprot->readString(_key92);
              std::string& _val93 = this->carrier[_key92];
              xfer += iprot->readString(_val93);
            }
            xfer += iprot->readMapEnd();
          }
          this->__isset.carrier = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      default:
        xfer += iprot->skip(ftype);
        break;
    }
    xfer += iprot->readFieldEnd();
  }

  xfer += iprot->readStructEnd();

  return xfer;
}

uint32_t RatingService_UploadRating_args::write(::apache::thrift::protocol::TProtocol* oprot) const {
  uint32_t xfer = 0;
  ::apache::thrift::protocol::TOutputRecursionTracker tracker(*oprot);
  xfer += oprot->writeStructBegin("RatingService_UploadRating_args");

  xfer += oprot->writeFieldBegin("req_id", ::apache::thrift::protocol::T_I64, 1);
  xfer += oprot->writeI64(this->req_id);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("movie_id", ::apache::thrift::protocol::T_STRING, 2);
  xfer += oprot->writeString(this->movie_id);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("rating", ::apache::thrift::protocol::T_I32, 3);
  xfer += oprot->writeI32(this->rating);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("carrier", ::apache::thrift::protocol::T_MAP, 4);
  {
    xfer += oprot->writeMapBegin(::apache::thrift::protocol::T_STRING, ::apache::thrift::protocol::T_STRING, static_cast<uint32_t>(this->carrier.size()));
    std::map<std::string, std::string> ::const_iterator _iter94;
    for (_iter94 = this->carrier.begin(); _iter94 != this->carrier.end(); ++_iter94)
    {
      xfer += oprot->writeString(_iter94->first);
      xfer += oprot->writeString(_iter94->second);
    }
    xfer += oprot->writeMapEnd();
  }
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldStop();
  xfer += oprot->writeStructEnd();
  return xfer;
}


RatingService_UploadRating_pargs::~RatingService_UploadRating_pargs() throw() {
}


uint32_t RatingService_UploadRating_pargs::write(::apache::thrift::protocol::TProtocol* oprot) const {
  uint32_t xfer = 0;
  ::apache::thrift::protocol::TOutputRecursionTracker tracker(*oprot);
  xfer += oprot->writeStructBegin("RatingService_UploadRating_pargs");

  xfer += oprot->writeFieldBegin("req_id", ::apache::thrift::protocol::T_I64, 1);
  xfer += oprot->writeI64((*(this->req_id)));
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("movie_id", ::apache::thrift::protocol::T_STRING, 2);
  xfer += oprot->writeString((*(this->movie_id)));
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("rating", ::apache::thrift::protocol::T_I32, 3);
  xfer += oprot->writeI32((*(this->rating)));
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("carrier", ::apache::thrift::protocol::T_MAP, 4);
  {
    xfer += oprot->writeMapBegin(::apache::thrift::protocol::T_STRING, ::apache::thrift::protocol::T_STRING, static_cast<uint32_t>((*(this->carrier)).size()));
    std::map<std::string, std::string> ::const_iterator _iter95;
    for (_iter95 = (*(this->carrier)).begin(); _iter95 != (*(this->carrier)).end(); ++_iter95)
    {
      xfer += oprot->writeString(_iter95->first);
      xfer += oprot->writeString(_iter95->second);
    }
    xfer += oprot->writeMapEnd();
  }
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldStop();
  xfer += oprot->writeStructEnd();
  return xfer;
}


RatingService_UploadRating_result::~RatingService_UploadRating_result() throw() {
}


uint32_t RatingService_UploadRating_result::read(::apache::thrift::protocol::TProtocol* iprot) {

  ::apache::thrift::protocol::TInputRecursionTracker tracker(*iprot);
  uint32_t xfer = 0;
  std::string fname;
  ::apache::thrift::protocol::TType ftype;
  int16_t fid;

  xfer += iprot->readStructBegin(fname);

  using ::apache::thrift::protocol::TProtocolException;


  while (true)
  {
    xfer += iprot->readFieldBegin(fname, ftype, fid);
    if (ftype == ::apache::thrift::protocol::T_STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
        if (ftype == ::apache::thrift::protocol::T_STRUCT) {
          xfer += this->se.read(iprot);
          this->__isset.se = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      default:
        xfer += iprot->skip(ftype);
        break;
    }
    xfer += iprot->readFieldEnd();
  }

  xfer += iprot->readStructEnd();

  return xfer;
}

uint32_t RatingService_UploadRating_result::write(::apache::thrift::protocol::TProtocol* oprot) const {

  uint32_t xfer = 0;

  xfer += oprot->writeStructBegin("RatingService_UploadRating_result");

  if (this->__isset.se) {
    xfer += oprot->writeFieldBegin("se", ::apache::thrift::protocol::T_STRUCT, 1);
    xfer += this->se.write(oprot);
    xfer += oprot->writeFieldEnd();
  }
  xfer += oprot->writeFieldStop();
  xfer += oprot->writeStructEnd();
  return xfer;
}


RatingService_UploadRating_presult::~RatingService_UploadRating_presult() throw() {
}


uint32_t RatingService_UploadRating_presult::read(::apache::thrift::protocol::TProtocol* iprot) {

  ::apache::thrift::protocol::TInputRecursionTracker tracker(*iprot);
  uint32_t xfer = 0;
  std::string fname;
  ::apache::thrift::protocol::TType ftype;
  int16_t fid;

  xfer += iprot->readStructBegin(fname);

  using ::apache::thrift::protocol::TProtocolException;


  while (true)
  {
    xfer += iprot->readFieldBegin(fname, ftype, fid);
    if (ftype == ::apache::thrift::protocol::T_STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
        if (ftype == ::apache::thrift::protocol::T_STRUCT) {
          xfer += this->se.read(iprot);
          this->__isset.se = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      default:
        xfer += iprot->skip(ftype);
        break;
    }
    xfer += iprot->readFieldEnd();
  }

  xfer += iprot->readStructEnd();

  return xfer;
}

void RatingServiceClient::UploadRating(const int64_t req_id, const std::string& movie_id, const int32_t rating, const std::map<std::string, std::string> & carrier)
{
  send_UploadRating(req_id, movie_id, rating, carrier);
  recv_UploadRating();
}

void RatingServiceClient::send_UploadRating(const int64_t req_id, const std::string& movie_id, const int32_t rating, const std::map<std::string, std::string> & carrier)
{
  int32_t cseqid = 0;
  oprot_->writeMessageBegin("UploadRating", ::apache::thrift::protocol::T_CALL, cseqid);

  RatingService_UploadRating_pargs args;
  args.req_id = &req_id;
  args.movie_id = &movie_id;
  args.rating = &rating;
  args.carrier = &carrier;
  args.write(oprot_);

  oprot_->writeMessageEnd();
  oprot_->getTransport()->writeEnd();
  oprot_->getTransport()->flush();
}

void RatingServiceClient::recv_UploadRating()
{

  int32_t rseqid = 0;
  std::string fname;
  ::apache::thrift::protocol::TMessageType mtype;

  iprot_->readMessageBegin(fname, mtype, rseqid);
  if (mtype == ::apache::thrift::protocol::T_EXCEPTION) {
    ::apache::thrift::TApplicationException x;
    x.read(iprot_);
    iprot_->readMessageEnd();
    iprot_->getTransport()->readEnd();
    throw x;
  }
  if (mtype != ::apache::thrift::protocol::T_REPLY) {
    iprot_->skip(::apache::thrift::protocol::T_STRUCT);
    iprot_->readMessageEnd();
    iprot_->getTransport()->readEnd();
  }
  if (fname.compare("UploadRating") != 0) {
    iprot_->skip(::apache::thrift::protocol::T_STRUCT);
    iprot_->readMessageEnd();
    iprot_->getTransport()->readEnd();
  }
  RatingService_UploadRating_presult result;
  result.read(iprot_);
  iprot_->readMessageEnd();
  iprot_->getTransport()->readEnd();

  if (result.__isset.se) {
    throw result.se;
  }
  return;
}

bool RatingServiceProcessor::dispatchCall(::apache::thrift::protocol::TProtocol* iprot, ::apache::thrift::protocol::TProtocol* oprot, const std::string& fname, int32_t seqid, void* callContext) {
  ProcessMap::iterator pfn;
  pfn = processMap_.find(fname);
  if (pfn == processMap_.end()) {
    iprot->skip(::apache::thrift::protocol::T_STRUCT);
    iprot->readMessageEnd();
    iprot->getTransport()->readEnd();
    ::apache::thrift::TApplicationException x(::apache::thrift::TApplicationException::UNKNOWN_METHOD, "Invalid method name: '"+fname+"'");
    oprot->writeMessageBegin(fname, ::apache::thrift::protocol::T_EXCEPTION, seqid);
    x.write(oprot);
    oprot->writeMessageEnd();
    oprot->getTransport()->writeEnd();
    oprot->getTransport()->flush();
    return true;
  }
  (this->*(pfn->second))(seqid, iprot, oprot, callContext);
  return true;
}

void RatingServiceProcessor::process_UploadRating(int32_t seqid, ::apache::thrift::protocol::TProtocol* iprot, ::apache::thrift::protocol::TProtocol* oprot, void* callContext)
{
  void* ctx = NULL;
  if (this->eventHandler_.get() != NULL) {
    ctx = this->eventHandler_->getContext("RatingService.UploadRating", callContext);
  }
  ::apache::thrift::TProcessorContextFreer freer(this->eventHandler_.get(), ctx, "RatingService.UploadRating");

  if (this->eventHandler_.get() != NULL) {
    this->eventHandler_->preRead(ctx, "RatingService.UploadRating");
  }

  RatingService_UploadRating_args args;
  args.read(iprot);
  iprot->readMessageEnd();
  uint32_t bytes = iprot->getTransport()->readEnd();

  if (this->eventHandler_.get() != NULL) {
    this->eventHandler_->postRead(ctx, "RatingService.UploadRating", bytes);
  }

  RatingService_UploadRating_result result;
  try {
    iface_->UploadRating(args.req_id, args.movie_id, args.rating, args.carrier);
  } catch (ServiceException &se) {
    result.se = se;
    result.__isset.se = true;
  } catch (const std::exception& e) {
    if (this->eventHandler_.get() != NULL) {
      this->eventHandler_->handlerError(ctx, "RatingService.UploadRating");
    }

    ::apache::thrift::TApplicationException x(e.what());
    oprot->writeMessageBegin("UploadRating", ::apache::thrift::protocol::T_EXCEPTION, seqid);
    x.write(oprot);
    oprot->writeMessageEnd();
    oprot->getTransport()->writeEnd();
    oprot->getTransport()->flush();
    return;
  }

  if (this->eventHandler_.get() != NULL) {
    this->eventHandler_->preWrite(ctx, "RatingService.UploadRating");
  }

  oprot->writeMessageBegin("UploadRating", ::apache::thrift::protocol::T_REPLY, seqid);
  result.write(oprot);
  oprot->writeMessageEnd();
  bytes = oprot->getTransport()->writeEnd();
  oprot->getTransport()->flush();

  if (this->eventHandler_.get() != NULL) {
    this->eventHandler_->postWrite(ctx, "RatingService.UploadRating", bytes);
  }
}

::apache::thrift::stdcxx::shared_ptr< ::apache::thrift::TProcessor > RatingServiceProcessorFactory::getProcessor(const ::apache::thrift::TConnectionInfo& connInfo) {
  ::apache::thrift::ReleaseHandler< RatingServiceIfFactory > cleanup(handlerFactory_);
  ::apache::thrift::stdcxx::shared_ptr< RatingServiceIf > handler(handlerFactory_->getHandler(connInfo), cleanup);
  ::apache::thrift::stdcxx::shared_ptr< ::apache::thrift::TProcessor > processor(new RatingServiceProcessor(handler));
  return processor;
}

void RatingServiceConcurrentClient::UploadRating(const int64_t req_id, const std::string& movie_id, const int32_t rating, const std::map<std::string, std::string> & carrier)
{
  int32_t seqid = send_UploadRating(req_id, movie_id, rating, carrier);
  recv_UploadRating(seqid);
}

int32_t RatingServiceConcurrentClient::send_UploadRating(const int64_t req_id, const std::string& movie_id, const int32_t rating, const std::map<std::string, std::string> & carrier)
{
  int32_t cseqid = this->sync_.generateSeqId();
  ::apache::thrift::async::TConcurrentSendSentry sentry(&this->sync_);
  oprot_->writeMessageBegin("UploadRating", ::apache::thrift::protocol::T_CALL, cseqid);

  RatingService_UploadRating_pargs args;
  args.req_id = &req_id;
  args.movie_id = &movie_id;
  args.rating = &rating;
  args.carrier = &carrier;
  args.write(oprot_);

  oprot_->writeMessageEnd();
  oprot_->getTransport()->writeEnd();
  oprot_->getTransport()->flush();

  sentry.commit();
  return cseqid;
}

void RatingServiceConcurrentClient::recv_UploadRating(const int32_t seqid)
{

  int32_t rseqid = 0;
  std::string fname;
  ::apache::thrift::protocol::TMessageType mtype;

  // the read mutex gets dropped and reacquired as part of waitForWork()
  // The destructor of this sentry wakes up other clients
  ::apache::thrift::async::TConcurrentRecvSentry sentry(&this->sync_, seqid);

  while(true) {
    if(!this->sync_.getPending(fname, mtype, rseqid)) {
      iprot_->readMessageBegin(fname, mtype, rseqid);
    }
    if(seqid == rseqid) {
      if (mtype == ::apache::thrift::protocol::T_EXCEPTION) {
        ::apache::thrift::TApplicationException x;
        x.read(iprot_);
        iprot_->readMessageEnd();
        iprot_->getTransport()->readEnd();
        sentry.commit();
        throw x;
      }
      if (mtype != ::apache::thrift::protocol::T_REPLY) {
        iprot_->skip(::apache::thrift::protocol::T_STRUCT);
        iprot_->readMessageEnd();
        iprot_->getTransport()->readEnd();
      }
      if (fname.compare("UploadRating") != 0) {
        iprot_->skip(::apache::thrift::protocol::T_STRUCT);
        iprot_->readMessageEnd();
        iprot_->getTransport()->readEnd();

        // in a bad state, don't commit
        using ::apache::thrift::protocol::TProtocolException;
        throw TProtocolException(TProtocolException::INVALID_DATA);
      }
      RatingService_UploadRating_presult result;
      result.read(iprot_);
      iprot_->readMessageEnd();
      iprot_->getTransport()->readEnd();

      if (result.__isset.se) {
        sentry.commit();
        throw result.se;
      }
      sentry.commit();
      return;
    }
    // seqid != rseqid
    this->sync_.updatePending(fname, mtype, rseqid);

    // this will temporarily unlock the readMutex, and let other clients get work done
    this->sync_.waitForWork(seqid);
  } // end while(true)
}

} // namespace


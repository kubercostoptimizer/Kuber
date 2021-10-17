def timeout_command(command, timeout, output):
  """call shell-command and either return its output or kill it
  if it doesn't normally exit within timeout seconds and return None"""
  import subprocess, datetime, os, time, signal
  start = datetime.datetime.now()
  if not output:
     process = subprocess.Popen(command, stderr=subprocess.STDOUT,stdout=subprocess.PIPE,shell=True)
  else:
     process = subprocess.Popen(command, shell=True)
     
  while process.poll() is None:
    time.sleep(0.1)
    now = datetime.datetime.now()
    #print (now - start).seconds
    if (now - start).seconds > timeout:
      print "Timeout process killed"
      os.kill(process.pid, signal.SIGKILL)
      os.waitpid(-1, os.WNOHANG)
      return None
  return None #process.stdout.read()
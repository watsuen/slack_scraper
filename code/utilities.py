import os, errno


# http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc: # Python >2.5
      if exc.errno == errno.EEXIST and os.path.isdir(path):
        pass
      else: raise

def is_path(path):
  return os.path.isdir(path)

# lists both paths and files
def list_path(path):
  if is_path(path):
    return [f for f in os.listdir(path)]
  return []
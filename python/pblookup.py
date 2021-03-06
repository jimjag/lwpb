#!/usr/bin/env python

'''
  pblookup - use an index to lookup records in a protobuf stream
    currently only supports one index type: -i cdb
'''

import sys
import os
import getopt


def shift(L): e = L[0] ; del L[0:1] ; return e

def main():

  reader_format = 'pb'
  writer_format = 'pb'
  delim = '\t'
  fields = []
  key = None
  typename = ""
  pb2file = None
  indextype = None
  indexreader = None
  indexfile = None
  fin = None
  fout = sys.stdout
  infile = None
  verbose = 0

  opts, args = getopt.getopt(sys.argv[1:], 'R:W:F:d:p:k:i:x:t:m:v')

  for o, a in opts:
    if o == '-R':
      reader_format = a
    elif o == '-W':
      writer_format = a
    elif o == '-F':
      fields = a.split(',')
    elif o == '-d':
      delim = a
    elif o == '-p':
      pb2file = a
    elif o == '-m':
      typename = a
    elif o == '-k':
      key = a
    elif o == '-i':
      indextype = a
    elif o == '-x':
      indexfile = a
    elif o == '-v':
      verbose += 1

  if key == None:
    raise Exception("missing key parameter, specify with -k")

  if not len(args):
    raise Exception("missing input data file argument")

  infile = shift(args)
  fin = file(infile)

  # create the index reader object

  if indextype == 'cdb':

    import cdb
    indexreader = cdb.init( indexfile )

  elif indextype == None:

    raise Exception("missing index type parameter, specify with -i")

  # initialize reader / writer codecs

  if pb2file:
    import lwpb.codec
    pb2codec = lwpb.codec.MessageCodec( pb2file=pb2file, typename=typename )

  if len(fields):
    import percent.codec
    txtcodec = percent.codec.PercentCodec( fields, delim )

  # create the stream reader

  if reader_format == 'pb':
    import lwpb.stream
    reader = lwpb.stream.StreamReader( fin, codec=pb2codec )
  elif reader_format == 'txt':
    import percent.stream
    reader = percent.stream.PercentCodecReader( fin, txtcodec )
  else:
    raise Exception("bad reader format")

  # create the stream writer

  if writer_format == 'pb':
    import lwpb.stream
    writer = lwpb.stream.StreamWriter( fout, codec=pb2codec )
  elif writer_format == 'txt':
    import percent.stream
    writer = percent.stream.PercentCodecWriter( fout, txtcodec )
  else:
    raise Exception("bad writer format")


  # lookup, read, and write records

  for line in sys.stdin:
    indexkey = line.strip('\r\n')

    for indexvalue in indexreader.getall(indexkey):
      offset = long( indexvalue )
      fin.seek( offset, os.SEEK_SET )
      record = reader.read()
      writer.write( record )

  return 0


if __name__ == '__main__':
  sys.exit(main())



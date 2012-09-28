#!/bin/bash

# a very simple cert authority
# now with JKS support!
#
# Copyright 2011 Oracle
# christopher.johnson@oracle.com
#

# License agreement:
# ------------------
# This script is intended as a simple sample and/or for my own
# purposes. If you get any benefit from it then that's GREAT but there
# are NO warranties and NO support. If this script burns down your
# house, chases your dog away, kills your houseplants and spoils your
# milk please don't say I didn't warn you.


# You should probably use a better passphrase than this
PASSPHRASE=ABcd1234

baseAnswers() {
    echo US
    echo Anywhere
    echo Anycity
    echo AnyOrg
    echo A-Team
    echo $1
    echo root@127.0.0.1
}

answers() {
    baseAnswers $1
    echo ''
    echo ''
}

# No need to edit past here

createderfiles() {
    echo Creating .der files for $1

    openssl pkcs8 -topk8 -nocrypt -in $1.key -inform PEM -out $1.key.der -outform DER
    openssl x509 -in $1.crt -inform PEM -out $1.crt.der -outform DER
}


# better safe than sorry
umask 077

# these next two lines figure out where the script is on disk
SCRIPTPATH=`readlink -f $0`
SCRIPTDIR=`dirname $0`

# find keytool in our path
KEYTOOL=`which keytool`
if [ "$KEYTOOL" == "" ] ; then
    echo "keytool command not found. Update your path if you want this"
    echo "tool to create JKS files as well as PEM format files"
fi

# if you're running this from somewhere else...
if [  $SCRIPTDIR != "."    -a   $SCRIPTDIR != $PWD  ]; then
    # then CD to that directory
    cd $SCRIPTDIR
    if [ "$KEYTOOL" == "" ]; then
 echo "Output files (.crt, .key) will be placed in $PWD"
    else
 echo "Output files (.crt, .key, .der and .jks) will be placed in $PWD"
    fi
fi

if [ ! -e ca.crt -o ! -e ca.key ]; then
    rm -f ca.crt ca.key ca.p12
    echo "Creating cert authority key & certificate"
    baseAnswers "My Cert Authority" | openssl req -newkey rsa:1024 -keyout ca.key -nodes -x509 -days 365 -out ca.crt 2> /dev/null
fi

if [ "$KEYTOOL" != "" ] ; then
    if [ ! -e ca.crt.der -o ! -e ca.key.der -o ! -e ca.jks ]; then
        # convert to der
 createderfiles ca

        # we actually don't need/want the ca.key.der but there's no
        # harm in leaving it around since the .key file is here anyway

 echo "Creating ca.jks"
        # import the CA certificate into the JKS file marking it as trusted
 keytool -import -noprompt -trustcacerts \
     -alias ca \
     -file ca.crt.der \
     -keystore ca.jks \
     -storetype JKS \
     -storepass $PASSPHRASE \
     2> /dev/null
    fi
fi

if [ $# -eq 0 ] ; then
    echo "This script creates one or more certificates."
    echo "Provide one or more certificate CNs on the command line."
    echo "Usage: `basename $0` <certcn> [certcn [...]]"
    exit -1
fi

for certCN in $@ ; do
    echo Certificate for CN \"$certCN\"
    echo =============================================

    KEY=$certCN.key
    CRT=$certCN.crt
    REQ=$certCN.req
    P12=$certCN.p12
    JKS=$certCN.jks

    # files we can delete later
    KEYDER=$KEY.der
    CRTDER=$CRT.der

    ABORT=0
    if [ -e $KEY ] ; then
 echo " ERROR: Key file $KEY already exists"
 ABORT=1
    fi
    if [ -e $REQ ] ; then
 echo " ERROR: Request file $REQ already exists"
 ABORT=1
    fi
    if [ -e $CRT ] ; then
 echo " ERROR: Certificate file $CRT already exists"
 ABORT=1
    fi
    
    if [ $ABORT -eq 1 ] ; then
 echo ''
 echo "If you wish to recreate a certificate for you must delete"
 echo "any preexisting files for that CN before running this script."
 echo ''
 echo ''
    else
 answers $certCN | openssl req -newkey rsa:1024 -keyout $KEY -nodes -days 365 -out $REQ  2> /dev/null
 
        # at this point we have a key file, but the cert is not signed by the CA
 openssl x509 -req -in $REQ -out $CRT -days 365 -CA ca.crt -CAkey ca.key -CAcreateserial -CAserial ca.serial -days 365 2> /dev/null

 # We now have a req, key and crt files which contain PEM format
 # x.509 certificate request
 # x.509 private key
 # x.509 certificate
 # respectively.

 echo "Certificate created."
 ls -l $KEY $REQ $CRT
 
 echo 'Certificate information:'
 openssl x509 -in $CRT -noout -issuer -subject -serial

 # generate a pkcs12 file
 openssl pkcs12 -export -in $CRT -inkey $KEY -certfile ca.crt -name $certCN -out $P12 -password pass:$PASSPHRASE -nodes

 echo P12 info:
 ls -l $P12
 #openssl pkcs12 -in $P12 -info -password pass:$PASSPHRASE -passin pass:$PASSPHRASE -nodes

 # if we have keytool we also need to create a jks file
 if [ "$KEYTOOL" != "" ] ; then
     echo "Will create JKS file as well..."
     createderfiles $certCN
     
     echo "Creating $JKS"
     # step 1: copy the CA keystore into the new one
     cp ca.jks $JKS

            # step 2: take the pkcs12 file and import it right into a JKS
            keytool -importkeystore \
  -deststorepass $PASSPHRASE \
  -destkeypass $PASSPHRASE \
  -destkeystore $JKS \
  -srckeystore $P12 \
  -srcstoretype PKCS12 \
  -srcstorepass $PASSPHRASE \
  -alias $certCN

     ls -l $JKS
     
     keytool -list -keystore $JKS -storepass $PASSPHRASE
 fi
 
    fi
    
done

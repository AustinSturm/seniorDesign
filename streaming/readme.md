## Description

 The client streams to the nginx relay which rebroadcasts the stream out for any user on that defined path. The rest server should communicate what path the stream will be on for each device, some unique stream identifier. EX: rtmp://host/rtmp/xxxx-yyyy-zzzz-dddd-1111-0033-<front/rear> The mobile application can tune to that broadcast via that url.

 Issues:
   Latency as well as no authentication on streams this way only security is making it difficult to guess a stream id.

## Requirements
Server:
   nginx
   nginx-rtmp-module

Client:
   ffmpeg or avconv

## Setup
Server:

Build Utilities
    sudo apt-get install build-essential libpcre3 libpcre3-dev libssl-dev
On Amazon Linux:

    sudo yum install git gcc make pcre-devel openssl-devel
Make and CD to build directory (home)

    sudo mkdir ~/build && cd ~/build
Download & unpack latest nginx-rtmp (you can also use http)

    sudo git clone git://github.com/arut/nginx-rtmp-module.git
Download & unpack nginx (you can also use svn)

    sudo wget http://nginx.org/download/nginx-1.12.0.tar.gz
    sudo tar xzf nginx-1.12.0.tar.gz
    cd nginx-1.12.0
Build nginx with nginx-rtmp

    sudo ./configure --with-http_ssl_module --add-module=../nginx-rtmp-module
    sudo make
    sudo make install
Start nginx Server
    sudo /usr/local/nginx/sbin/nginx

Modify /user/local/nginx/conf/nginx.conf with configuration provided


Client:
   sudo apt-get install libav-tools
   # note following command needs to be optimized TODO
   avconv -f video4linux2 -i /dev/video0 -vcodec mpeg2video -r 60 -f rtp rtp://<serverIp>:1234/test/<uid> &

## Usage

Server:

Client:

   avconv .... -f ... rtmp://awshost.com/test/<id>

## Statistics

FPS =
Resolution =
Latency =

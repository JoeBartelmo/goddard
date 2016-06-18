var cli = require('cli');
var exec = require('child_process').exec;
var fs = require('fs'); 

//I don't like any of this...
var generateVLCStreamCommands = function generateVLCStreamCommands(options, cameras) {
  //like srsly kill me
  var vlcCommands = [];
  for(var index in cameras) { 
    vlcCommands.push("cvlc "+ (options.verbose ? '-vvv' : '')+"v4l2://"+cameras[index]+":width="+options.width+":height="+options.height+":fps="+options.fps+" --live-caching 200 --sout '#transcode{vcodec=h264,venc=x264{preset=ultrafast}vb="+options.bitrate+",acodec=none}:duplicate{dst=file{dst=/phobos/stream_archive/"+ options.filename+index +".mp4},dst=rtp{sdp=rtsp://:"+(parseInt(options.port)+parseInt(index))+"/}}'");

  cli.info('Opened New Stream on Port: ' + (parseInt(options.port) + parseInt(index)));
  }
  return vlcCommands;
}

var killPID = function killPID(pid) {
  if(pid.length > 0) {
    var command = 'kill -9 ' + pid;
    exec(command, function callback(err, result) {
        var result = (err || result || 'success').toString();
        if(result.indexOf('No such process') > -1) {
          result = 'Was already deleted';
        }
        cli.info('Result of [' + command + ']: ' + result);
    });
  } 
}

//Manually reads in the pids file and deletes all pids
var closeOpenStreams = function closeOpenstreams() {
  var pids = fs.readFileSync('do-not-delete-manually.hyperloop');
  if(pids && pids.length > 1) {
    pids = pids.toString().split("\n");
    //cli.info('Manually Kiling the following pids: ' + pids);
    for(var index in pids) {
      killPID(pids[index]);
    }
  }
  else {
    cli.info('Could not read pids file (do-not-delete-manually)');
  }

  return 0;  
}


cli.parse({
  width: ['w', 'Width of video to streams', 'int', 640],
  height: ['h', 'Height of the video streams', 'int', 480],
  bitrate: ['b', 'Requested bitrate from streams', 'int', 4000],
  filename: ['f', 'Filename base to write the streams (test#.mp4)', 'string', 'test'],
  fps: ['fps', 'Frames per second that the camera should attempt to capture', 'int', 45],
  port: ['p', 'Default starting port to broadcast over -- increments by 1 for each camera', 'int', 8554],
  verbose: [false, 'If on, will log out all of VLCs garbage', 'bool', false],
  close: [false, 'When a stream is launched the Processs ID is tracked, if there is an interrupt of communication between client and server, this will explicitly close any opened streams']
});

cli.main(function mainEntryPoint(args, options) {
  
  //if the close option is set, we don't even bother with reading, we try to open
  //up pid file, and read in the pids, afterwards we delete the pid file and 
  //move on
  if(options.close) {
    closeOpenStreams();
  }
  else {
    //start by grabbing all camera
    fs.readdir('/dev/', function getCameras(err, files) {
      if(err) {
        cli.fatal(err);
      }
      var cameras = [];
      for(var index in files) {
        if(files[index].indexOf('video') > -1) {
          cameras.push('/dev/' + files[index]);
        }
      }
      cli.info('Found Cameras: ' + cameras);
      var commands = generateVLCStreamCommands(options, cameras);
    
      for(var index in commands) {
        exec(commands[index]);
      }
     
      //just use a pipe so i don't have to launch an fs writer
      exec('pgrep -f vlc > do-not-delete-manually.hyperloop', function(err, pids, stderr) {
        if(err) {
           cli.fatal('Could not obtain the VLC pids');
        }
      });
    });
  }
});


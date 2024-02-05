#import "ios_player.h"
#import "vk_session.h"



@implementation IOS_player
- (id) init {
    if(self = [super init]) {
        BOOL _isPlaying=NO;
        // create audio session
        AVAudioSession *session = [AVAudioSession sharedInstance];
        [session setCategory:AVAudioSessionCategoryPlayback error:NULL];
        [session setActive:YES error:NULL];
        // setup lock screen player
        MPRemoteCommandCenter *commandCenter = [MPRemoteCommandCenter sharedCommandCenter];
        
        [commandCenter.playCommand addTargetWithHandler:^MPRemoteCommandHandlerStatus(MPRemoteCommandEvent * _Nonnull event) {
                [self play];
                return MPRemoteCommandHandlerStatusSuccess;
            }];
                                            
        [commandCenter.pauseCommand addTargetWithHandler:^MPRemoteCommandHandlerStatus(MPRemoteCommandEvent * _Nonnull event) {
            [self pause];
            return MPRemoteCommandHandlerStatusSuccess;
        }];

        [commandCenter.previousTrackCommand addTargetWithHandler:^MPRemoteCommandHandlerStatus(MPRemoteCommandEvent * _Nonnull event) {
            [self prev];
            return MPRemoteCommandHandlerStatusSuccess;
        }];
        
        [commandCenter.nextTrackCommand addTargetWithHandler:^MPRemoteCommandHandlerStatus(MPRemoteCommandEvent * _Nonnull event) {
            [self next];
            return MPRemoteCommandHandlerStatusSuccess;
        }];
        
        [commandCenter.changePlaybackPositionCommand addTargetWithHandler:^MPRemoteCommandHandlerStatus(MPRemoteCommandEvent * _Nonnull event) {
            [self seek: ((MPChangePlaybackPositionCommandEvent*)event).positionTime];
            
            return MPRemoteCommandHandlerStatusSuccess;
        }];
        // Importan for background playback.
        [[UIApplication sharedApplication] beginReceivingRemoteControlEvents];
    }
    return self;
}

- (void) loadPlaylist:(NSMutableArray *)trackList key:(int)key{
    // Do initialization.
    _trackList = trackList;
    _key = key;
    _track = [_trackList objectAtIndex:_key];
    _isStream = NO;
    // Init player instance.
    [self initPlayer:NULL cookies:NULL];
}

- (void) loadVKPlaylist:(NSMutableArray *)trackList key:(int)key cookies:(NSMutableArray *)cookiesList uid:(int)uid{
    // Do initialization
    _session = [VKsessionManager sharedInstance:self];
    _uid = uid;
    _trackList = trackList;
    _key = key;
    _track = [_trackList objectAtIndex:_key];
    _isStream = YES;
    // Init player instance.
    [self initPlayer:NULL cookies:cookiesList];
}

- (void)initPlayer:(NSURL *) url cookies:(NSMutableArray *)cookiesList{
    if (url) {
        NSLog(@"init player with url:%@",url);
        _HLSplayer = [[AVPlayer alloc] initWithURL:url];
        _HLSplayer.preventsDisplaySleepDuringVideoPlayback=NO;
        //register event on end of audio playback
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(HLSaudioPlayerDidFinishPlaying:) name:AVPlayerItemDidPlayToEndTimeNotification object:[_HLSplayer currentItem]];
        
        [self play];
        // Do any additional setup after loading the lock screen player view.
        [self refresh];
        return;
    }
    //stop previous initiated playback
    [self stop];
    [self seek:0.0];
    // init player instance
    if (!_isStream){
        // set path for file
        NSURL *url = [[NSURL alloc] initFileURLWithPath:[_track objectAtIndex:0]];
        NSLog(@"init player with url:%@",url);
        _player = [[AVAudioPlayer alloc] initWithContentsOfURL: url error:NULL];
        // Register event on end of audio playback.
        [_player setDelegate: self];
        [self play];
        // Do any additional setup after loading the lock screen player view.
        [self refresh];
        
    }else{
        NSLog(@"Audio hash arrived: %@",[_track objectAtIndex:0]);
        [_session getLink:cookiesList audioHash:[_track objectAtIndex:0]];
    }
}

- (void)HLSaudioPlayerDidFinishPlaying:(NSNotification *) notification{
    NSLog(@"Stream ended");
    _isPlaying = NO;
    [self next];
}

- (void)audioPlayerDidFinishPlaying:(AVAudioPlayer *)player successfully:(BOOL)flag{
    printf("Audio has ended");
    _isPlaying=NO;
    [self next];
}

- (void)seek: (double) t {
    if (_isStream){
        [_HLSplayer seekToTime:CMTimeMake(t*10000, 10000)];
    } else {
        _player.currentTime = t;
    }
    [self refresh];
}

- (double)get_pos{
    double pos = _isStream ? CMTimeGetSeconds(_HLSplayer.currentTime) : _player.currentTime;
    return pos;
}

- (double)get_len{
    double len = _isStream ? CMTimeGetSeconds(_HLSplayer.currentItem.duration) : _player.duration;
    return len;
}

- (NSDictionary *)get_info {
    double pos = [self get_pos];
    double len = [self get_len];
    if ((_track) && !([_track isEqual:@"EOL"]) && !(isnan(len)||isnan(pos))) {
        NSDictionary* info = @{
            @"key": [NSString stringWithFormat:@"%d", _key],
            @"file": [_track objectAtIndex:0],
            @"author": [_track objectAtIndex:1],
            @"song": [_track objectAtIndex:2],
            @"len": [NSNumber numberWithFloat: len],
            @"pos": [NSNumber numberWithFloat: pos],
            @"img": [_track objectAtIndex:3],
            @"status":[NSNumber numberWithBool: _isPlaying]
        };
        return info;
    } else {
        NSLog(@"No available track");
        return NULL;
    }
        
}
- (void)play {
    _isPlaying=YES;
    _isStream ? [_HLSplayer play] : [_player play];
    [self refresh];
}

- (void)pause {
    _isPlaying=NO;
    _isStream ? [_HLSplayer pause] : [_player pause];
    [self refresh];
}

-(void)stop{
    _isPlaying=NO;
    _isStream ? [_HLSplayer pause] : [_player stop];
}

-(void)prev{
    _key = _key-1;
    if (_key<0) {
        NSLog(@"List out of range");
        _key = _key + 1;
        return [self EOL];
    }
    _track = [_trackList objectAtIndex:_key];

    [self initPlayer:NULL cookies:NULL];
}

-(void)next{
    _key = _key+1;
    @try {
        if ([[_trackList objectAtIndex:_key] isEqual:@"EOL"]) {
            // end of list
            NSLog(@"List out of range");
            _key = _key - 1;
            return [self EOL];
            
        } else {
            _track = [_trackList objectAtIndex:_key];
            
        }
    }
    @catch (NSException *e){
        // list does not end until ending indentifier
        _key = _key-1;
        if (![_session isLoading] && _isStream){
            [_session loadMore];
        }
        return NULL;
    }

    // player instance
    [self initPlayer:NULL cookies:NULL];
}

- (void) EOL{
    [self pause];
    [self seek:0.0];
}

- (void)refresh {
    if (!(_track)||[_track isEqual:@"EOL"]){
        return;
    }

    if (_isStream){
        [_session loadAudioInfo];

    } else {
        UIImage *image = [UIImage imageWithContentsOfFile:[_track objectAtIndex:3]];
        NSDictionary* info = @{
            MPMediaItemPropertyArtwork:[[MPMediaItemArtwork alloc] initWithBoundsSize:image.size requestHandler:^UIImage * _Nonnull(CGSize size) {
                return image;
            }],
            MPMediaItemPropertyArtist: [_track objectAtIndex:1],
            MPMediaItemPropertyTitle: [_track objectAtIndex:2],
            MPNowPlayingInfoPropertyMediaType: @(MPMediaTypeMusic),
            MPMediaItemPropertyPlaybackDuration: @(_player.duration),
            MPNowPlayingInfoPropertyPlaybackRate: @(_isPlaying ? _player.rate : 0),
            MPNowPlayingInfoPropertyElapsedPlaybackTime: @(_player.currentTime)
        };
        MPNowPlayingInfoCenter.defaultCenter.nowPlayingInfo = info;
    }
}
@end

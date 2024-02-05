#import "vk_session.h"



@implementation Constants

NSString *const CHAR_SET = @"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN0PQRSTUVWXYZO123456789+/=";

NSString *const nextFromPattern = @"\\b\"nextFrom\":\"(.*?)\",\\b";

@end

@implementation VKsessionManager
- (id) init:(IOS_player *) player {
    self = [super init];
    if (self){
        _cookieManager = [CookieManager sharedInstance];
        _player = player;
        _uid = 0;
        _isLoading = NO;
        //configure session
        NSURLSessionConfiguration *conf = [NSURLSessionConfiguration defaultSessionConfiguration];
        _session = [NSURLSession sessionWithConfiguration:conf delegate:self delegateQueue:nil];
        
    }
    return self;
}

+ (VKsessionManager *)sharedInstance:(IOS_player *)player{
    // singleton
    static VKsessionManager *sharedInstanse = NULL;
    static dispatch_once_t isDispatched;
    dispatch_once(&isDispatched, ^{
        sharedInstanse = [[VKsessionManager alloc] init:player];

    });
    return sharedInstanse;
}

- (void) loadAudioInfo{
    NSURLSessionDownloadTask *imgTask = [_session downloadTaskWithURL:[NSURL URLWithString:[_player.track objectAtIndex:3]] completionHandler:^(NSURL * _Nullable location, NSURLResponse * _Nullable response, NSError * _Nullable error) {
        UIImage *image = [UIImage imageWithData:[NSData dataWithContentsOfURL:location]];

        NSDictionary* info = @{
            MPMediaItemPropertyArtwork:[[MPMediaItemArtwork alloc] initWithBoundsSize:image.size requestHandler:^UIImage * _Nonnull(CGSize size) {
                return image;
            }],
            MPMediaItemPropertyArtist: [_player.track objectAtIndex:1],
            MPMediaItemPropertyTitle: [_player.track objectAtIndex:2],
            MPNowPlayingInfoPropertyMediaType: @(MPMediaTypeMusic),
            MPMediaItemPropertyPlaybackDuration: @(CMTimeGetSeconds(_player.HLSplayer.currentItem.duration)),
            MPNowPlayingInfoPropertyPlaybackRate: @(_player.isPlaying ? _player.HLSplayer.rate : 0),
            MPNowPlayingInfoPropertyElapsedPlaybackTime: @(CMTimeGetSeconds(_player.HLSplayer.currentTime))
        };
        MPNowPlayingInfoCenter.defaultCenter.nowPlayingInfo = info;
    }];
    [imgTask resume];
}

- (void) loadSession:(NSMutableArray *)cookies audioHash:(NSString *)hash {
    // prepare cookies
    [_cookieManager clearCookies];
    [_cookieManager loadCookies:cookies];
    // auth request
    NSURLSessionDataTask *preLoadPage = [_session dataTaskWithURL:[NSURL URLWithString:@"https://vk.com/login"] completionHandler:^(NSData * _Nullable data, NSURLResponse * _Nullable response, NSError * _Nullable error) {
        NSLog(@"%@, %@",[response URL], [response URL].absoluteString);
        if ([[response URL].absoluteString containsString:@"/login"]){
            NSLog(@"Error appear");
        }else{
            NSLog(@"Session loaded with UID: %d",[_player uid]);
            [self getLink:NULL audioHash:hash];
        }
    }];
    [preLoadPage resume];
}

- (void) getLink:(NSMutableArray *)cookies audioHash:(NSString *)hash{
    // if session not loaded do set up
    if (_uid != [_player uid]) {
        NSLog(@"Load session with UID: %d",[_player uid]);
        _uid = [_player uid];
        [self loadSession:cookies audioHash:hash];

    } else {
        //configuring request to get mp3 link
        NSMutableURLRequest *request = [NSMutableURLRequest requestWithURL:[NSURL URLWithString:@"https://vk.com/al_audio.php?act=reload_audio"]];
        NSString *payload = [NSString stringWithFormat:@"al=1&ids=%@",hash];
        NSData *payloadData = [payload dataUsingEncoding:NSASCIIStringEncoding allowLossyConversion:YES];
        [request setHTTPMethod:@"POST"];
        [request setHTTPBody:payloadData];
        
        NSURLSessionDataTask *task = [_session dataTaskWithRequest:request completionHandler:^(NSData * _Nullable data, NSURLResponse * _Nullable response, NSError * _Nullable error) {
            // parse returned json
            NSString *resp = [[[NSString alloc] initWithData:data encoding:NSASCIIStringEncoding] substringFromIndex:4];
            NSData *jsonData = [resp dataUsingEncoding:NSUTF8StringEncoding];
            NSError *jsonError = NULL;
            id jsonResponse = [NSJSONSerialization JSONObjectWithData:jsonData options:NSJSONReadingAllowFragments error:&jsonError];
            if (jsonError){
                NSLog(@"%@",jsonError);
            }
            if ([jsonResponse isKindOfClass:[NSDictionary class]]){
                NSDictionary *json = jsonResponse;
                NSString *mp3_url = [json objectForKey:@"payload"][1][0][0][2];
                NSLog(@"mp3 link: %@",mp3_url);
                // encode mp3 link to m3u8 link
                NSURL *m3u8 = [self encodeLink:mp3_url];
                NSLog(@"m3u8 link: %@",m3u8);
                // init player with m3u8 link
                return [_player initPlayer:m3u8 cookies:NULL];
            } else {
                NSLog(@"Type error");
            }
        }];
        [task resume];
        
    }
}

- (NSURL *) encodeLink:(NSString *)mp3_url{
    NSArray *ii;
    NSString *eee;
    NSArray *f = [mp3_url componentsSeparatedByString:@"?extra="];

    NSArray *e = [f[1] componentsSeparatedByString:@"#"];
    NSString *i = [self _:e[1]];
    NSString *ee = [self _:e[0]];
    if (i){
        ii = [i componentsSeparatedByString:[NSString   stringWithFormat:@"%c", (char)9]];

    }
    else{
        ii = [NSArray array];
    }
    
    int s = (int)[ii count];
    for (int ss = s-1; ss>-1; --ss){
        NSMutableArray *a = [[ii[ss] componentsSeparatedByString:[NSString stringWithFormat:@"%c", (char)11 ]] mutableCopy];

        NSString *o = [a objectAtIndex:0];
        [a removeObjectAtIndex:0];
        [a addObject:ee];
        eee = [self c:o t:a[1] e:[a[0] intValue]];
    }
    NSURL *m3u8 = [[NSURL alloc] initWithString:eee];
    return m3u8;
}
- (NSString *) _: (NSString *) t{
    int e = 0;
    int o = 0;
    NSMutableString *s = [NSMutableString string];
    for (int j = 0; j < [t length]; j++){
        unichar c = [t characterAtIndex:j];
        NSString *i = [NSString stringWithCharacters:&c length:1 ];
        if (![CHAR_SET containsString:i]) {
            continue;
        }
        // find char index
        int ii = (int)[[[CHAR_SET componentsSeparatedByString:i] objectAtIndex:0] length];
        
        if (o%4 != 0) {
            e = 64*e + ii;
        } else {
            e = ii;
        }
        o += 1;
        if ((o-1)%4) {
            NSString *cc = [NSString stringWithFormat:@"%c", (char)(255 & e >> (-2*o&6))];

            s = [[s stringByAppendingString:cc] mutableCopy];
            
        }
    }
    return s;
}
- (NSString *) c:(NSString *) func t:(NSString *) t e:(int) e{
    if ([func  isEqual: @"v"]) {
        return [self v:t];
    }else if ([func  isEqual: @"r"]){
        return [self r:t e:e];
    }else if ([func  isEqual: @"s"]){
        return [self s:t e:e];
    }else if ([func  isEqual: @"i"]){
        return [self i:t e:e];
    }else if ([func isEqual:@"x"]){
        return [self x:t e:e];
    }
    return NULL;
}
- (NSString *) v:(NSString *) t{
    NSMutableString *reversedString = [NSMutableString string];
    NSInteger charIndex = [t length];
    while (charIndex > 0) {
        charIndex--;
        NSRange subStrRange = NSMakeRange(charIndex, 1);
        [reversedString appendString:[t substringWithRange:subStrRange]];
    }
    return reversedString;
}
- (NSString *) r:(NSString *)t e:(int) e{
    NSString *o = [CHAR_SET stringByAppendingString:CHAR_SET];
    // NSString to NSArray
    NSMutableArray <NSString *> *tt = @[].mutableCopy;
    [t enumerateSubstringsInRange:NSMakeRange(0, t.length) options:NSStringEnumerationByComposedCharacterSequences usingBlock:^(NSString * _Nullable substring, NSRange substringRange, NSRange enclosingRange, BOOL * _Nonnull stop) {
        [tt addObject:substring];
    }];

    for (int j = (int)[tt count]-1; j>-1; j--){
        // find char index
        int i = (int)([[[o componentsSeparatedByString:tt[j]] objectAtIndex:0] length] - 1);
        if (~i) {
            tt[j] = [o substringWithRange:NSMakeRange(i-e, 1-i+e)];
        }
    }
    return [tt componentsJoinedByString:@""];
}
- (NSString *) s:(NSString *) t e: (int) e{
    // NSString to NSArray
    NSMutableArray <NSString *> *tt = @[].mutableCopy;
    [t enumerateSubstringsInRange:NSMakeRange(0, t.length) options:NSStringEnumerationByComposedCharacterSequences usingBlock:^(NSString * _Nullable substring, NSRange substringRange, NSRange enclosingRange, BOOL * _Nonnull stop) {
        [tt addObject:substring];
    }];
    int i = (int)[tt count];
    NSMutableArray *o = [NSMutableArray array];
    if (i) {
        for (int j = i-1; j>-1; --j){
            e = (i * (j + 1)^e +j) % i;
            [o addObject:[NSNumber numberWithInteger: e]];
            
        }
        o = [[o reverseObjectEnumerator] allObjects];
        
        for (int j = 1; j<i; j++){
            [tt exchangeObjectAtIndex: j withObjectAtIndex:[o[i-1-j] intValue]];
        }
    }
    return [tt componentsJoinedByString:@""];
}
- (NSString *) i:(NSString *) t e:(int) e{
    return [self s:t e:(e^_uid)];
}
- (NSString *) x:(NSString *) t e:(int) e{
    int ee = [[[NSString stringWithFormat:@"%d",e] substringToIndex:1] intValue];

    NSMutableArray *tt = [NSMutableArray array];
    for (int j = 0; j<[t length]; j++){

        [tt addObject:[NSString stringWithFormat:@"%c", (char)((int)[t characterAtIndex:j]^ee)]];
    }
    return [tt componentsJoinedByString:@""];
}

@end

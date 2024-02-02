#import "audio_loader.h"



void addUIAction(AsyncUpdateUIBlock asyncUpdateUIBlock) {
    dispatch_async(dispatch_get_main_queue(), ^{
        asyncUpdateUIBlock();
    });
}


@implementation audioLoader {
    Statistics *statistics;
}

- (id) init {
    if(self = [super init]) {
        _isExecuting = NO;
        _taskList = [[NSMutableArray alloc] init];
        statistics = NULL;
        _duration = 0;
        _durationRegexp = [NSRegularExpression regularExpressionWithPattern:@"\\b^([0-9]+):([0-9]+):([0-9]+).([0-9]+)$\\b" options:0 error:NULL];
    }
    return self;
}

- (void) loadVK: (NSString *) m3u8 fileName:(NSString *)path key:(NSString *)key {
    [_taskList addObject:[@{@"key":key,@"link":m3u8,@"path":path,@"progress":@"0"} mutableCopy]];
    NSLog(@"New task arrived. Total number of tasks to execute:%lu",(unsigned long)[_taskList count]);

    if (!_isExecuting){
        _isExecuting = YES;
        [self ffmpegEx];
    }
}

- (void)endTask{
    [_taskList removeObjectAtIndex:0];
}

- (void)cancelTask{
    // TODO
}

- (void) ffmpegEx{
    NSString *m3u8 = [[_taskList objectAtIndex:0] objectForKey:@"link"];
    NSString *path = [[_taskList objectAtIndex:0] objectForKey:@"path"];
    // Form ffmpeg query
    NSString *q = [NSString stringWithFormat:@"-http_persistent false -i %@ %@ -v 32 -y",m3u8,path];
    // Start ffmpeg
    FFmpegSession *session = [FFmpegKit executeAsync:q
    withCompleteCallback:^(FFmpegSession *session){
        NSLog(@"Task done");
        [self endTask];
        SessionState state = [session getState];
        ReturnCode *retCode = [session getReturnCode];
 
        if ([ReturnCode isSuccess:retCode]){
            NSLog(@"Encode complit successfully in %ld millsec", [session getDuration]);
        }else{
            NSLog(@"Encode failed");
        }
        
        if ([_taskList count] != 0){
            // next to go
            NSLog(@"Execute next");
            return [self ffmpegEx];
            
        }else{
            // no task to execute left
            NSLog(@"Out of tasks");
            _isExecuting = NO;
        }
        
    }
                
    withLogCallback:^(Log *log) {
        // NSLog(@"[FFMPEG log message]:%@",[log getMessage]);
        if ([_durationRegexp numberOfMatchesInString:[log getMessage] options:0 range:NSMakeRange(0, [[log getMessage] length])] == 1){
            NSLog(@"Duration is:%@", [log getMessage]);
            NSArray *num_arr = [[[[[log getMessage] stringByReplacingOccurrencesOfString:@"." withString:@""] componentsSeparatedByString:@":"] reverseObjectEnumerator] allObjects];
            _duration = 0;
            int i = 2;
            do {
                long num = [num_arr[i] floatValue];
                _duration += (i!=0) ? 60*i*num : num/100.0;
                i--;
            }while (i >= 0);
        }
    }
    withStatisticsCallback:^(Statistics *statistics) {
        addUIAction(^{
            self->statistics = statistics;
            [self updateProgressBar];
        });
    }];
    NSLog(@"FFmpeg process started with session id: %ld",[session getSessionId]);
    
}

- (NSMutableArray *) get_info{
    return _taskList;
}

-(void) updateProgressBar{
    if (statistics==NULL || [statistics getTime] < 0){
        return;
    }
    if ([_taskList count] != 0){
        // Calculate progress of current task.
        double timeInMS = [statistics getTime]/1000;
        int persentage = timeInMS*100/_duration;
        NSLog(@"Audio duration: %ld Encoding audio progress: %% %d", _duration,persentage);
        [[_taskList objectAtIndex:0] setObject:[NSString stringWithFormat:@"%d", persentage] forKey:@"progress"];
    }
}

@end

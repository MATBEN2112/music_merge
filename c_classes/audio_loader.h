#import <AVFoundation/AVFoundation.h>
#import <ffmpegkit/FFmpegKit.h>



typedef  void (^AsyncUpdateUIBlock)(void);

extern void addUIAction(AsyncUpdateUIBlock asyncUpdateUIBlock);

@interface audioLoader: NSObject
@property (nonatomic) long duration;
@property (nonatomic, assign) NSRegularExpression *durationRegexp;
@property (nonatomic) int taskCount;
@property (nonatomic) BOOL isExecuting;
@property (nonatomic, assign) NSMutableArray *taskList;
- (void)loadVK: (NSString *) m3u8 fileName: (NSString *) path key: (NSString *) key;
- (NSMutableArray *) get_info;
@end

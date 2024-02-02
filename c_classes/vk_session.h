#import "ios_player.h"
#import "cookie.h"



@interface Constants : NSObject
extern NSString *const CHAR_SET;
extern NSString *const durationPattern;
@end

@interface VKsessionManager : NSObject <NSURLSessionDelegate>
@property (strong, nonatomic) CookieManager *cookieManager;
@property (strong, nonatomic) IOS_player *player;
@property (strong, nonatomic) NSURLSession *session;
@property (nonatomic) int uid;
@property (nonatomic) BOOL isLoading;
+ (VKsessionManager *) sharedInstance:(IOS_player *) player;
- (void) loadMore;
- (void) loadAudioInfo;
- (void) loadSession: (NSMutableArray *) cookies audioHash: (NSString *) hash;
- (void) getLink: (NSMutableArray *) cookies audioHash: (NSString *) hash;
- (NSURL *) encodeLink: (NSString *) mp3_url;
- (NSString*) _: (NSString *) t;
- (NSString*) c: (NSString *) func t: (NSString *) t e: (int) e;
- (NSString*) v: (NSString *) t;
- (NSString*) r: (NSString *) t e: (int) e;
- (NSString*) s: (NSString *) t e: (int) e;
- (NSString*) i: (NSString *) t e: (int) e;
- (NSString*) x: (NSString *) t e: (int) e;

@end

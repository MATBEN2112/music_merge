#import <AVFoundation/AVFoundation.h>

@interface CookieManager : NSObject
@property (strong, nonatomic) NSHTTPCookieStorage *cookieStorage;
+ (CookieManager *) sharedInstance;
- (void) loadCookies: (NSMutableArray *) cookies;
- (void) clearCookies;

@end


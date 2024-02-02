#import "cookie.h"



@implementation CookieManager
- (id) init{
    self = [super init];
    if (self){
        _cookieStorage = [NSHTTPCookieStorage sharedHTTPCookieStorage];
        [_cookieStorage setCookieAcceptPolicy:NSHTTPCookieAcceptPolicyAlways];
        
    }
    return self;
}
+ (CookieManager *)sharedInstance{
    // singleton
    static CookieManager *sharedInstanse = NULL;
    static dispatch_once_t isDispatched;
    dispatch_once(&isDispatched, ^{
        sharedInstanse = [[CookieManager alloc] init];

    });
    return sharedInstanse;
}

- (void) loadCookies:(NSMutableArray *)cookies{
    for (NSArray *cookie in cookies){
        // cookie properties
        NSDictionary *properties = [NSDictionary dictionaryWithObjectsAndKeys:cookie[2], NSHTTPCookieDomain, cookie[0], NSHTTPCookieName, cookie[1], NSHTTPCookieValue, cookie[3], NSHTTPCookiePath,  nil];
        // cookie object
        NSHTTPCookie *cookie = [[NSHTTPCookie alloc] initWithProperties:properties];
        // set cookie
        [_cookieStorage setCookie:cookie];
    }
}

- (void) clearCookies{
    // clean previusly loaded cookies
    for (NSHTTPCookie *cookie in _cookieStorage.cookies){
        [_cookieStorage deleteCookie:cookie];
    }
}

@end

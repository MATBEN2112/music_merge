#import <MediaPlayer/MediaPlayer.h>
#import <AVFoundation/AVFoundation.h>



typedef  void (^AsyncUpdateUIBlock)(void);

extern void addUIAction(AsyncUpdateUIBlock asyncUpdateUIBlock);

@interface IOS_player: NSObject <AVAudioPlayerDelegate>
@property (nonatomic) bool isPlaying;
@property (nonatomic) bool isStream;
@property (strong, nonatomic) id session;
@property (strong, nonatomic) AVAudioPlayer *player;
@property (strong, nonatomic) AVPlayer *HLSplayer;
@property (nonatomic) int uid;
@property (nonatomic,assign) NSString *sectionID;
@property (nonatomic,assign) NSString *nextFrom;
@property (nonatomic,assign) NSMutableArray *trackList;
@property (nonatomic) int key;
@property (nonatomic,assign) NSArray *track;
- (void)initPlayer:(NSURL *) url cookies:(NSMutableArray *)cookiesList;
- (void)loadPlaylist: (NSMutableArray *)trackList key: (int)key;
- (void)loadVKPlaylist: (NSMutableArray *)trackList key: (int)key cookies: (NSMutableArray *)cookiesList uid:(int) uid sectionID:(NSString *) sectionID nextFrom:(NSString *) nextFrom;
- (void)play;
- (void)pause;
- (void)next;
- (void)prev;
- (void)EOL;
- (void)seek: (double) t;
- (double)get_pos;
- (double)get_len;
- (NSDictionary *)get_info;
- (void)refresh;
@end


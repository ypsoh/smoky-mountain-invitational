/* ============================================================
   THE SMOKY MOUNTAIN INVITATIONAL — SINGLE SOURCE OF TRUTH
   September 12-13, 2026

   DURING THE TRIP you only ever touch the SCORES block at the
   bottom. Type the strokes, save the file, refresh match.html.
   That is the entire workflow: no build, no server, no network.

   Loaded as a classic script (never type="module", which is
   CORS-blocked from file://). Everything below is a global.
   ============================================================ */

/* Everyone plays their full strokes. Simple to explain on the
   first tee, which is the only place it matters. Set this to 0.90
   if you ever want to trim the high handicaps back a little. */
var ALLOWANCE  = 1.00;
var POINTS_WIN = 1;
var POINTS_TIE = 0.5;

/* Team mulligans, per team, per round. Use them whenever you like.
   Run out and you can buy more -- see PRICE, which goes in the pot. */
var MULLIGANS = { perTeamPerRound: 6, extraPrice: 10 };

var TRIP = {
  name:   'The Smoky Mountain Invitational',
  nameKo: '스모키 마운틴 인비테이셔널',
  dates:  'September 12-13, 2026',
  datesKo: '2026년 9월 12일 - 13일',
  cancelDeadline: '2026-09-11T12:10:00-04:00',
  origin: { label: 'Knoxville, TN', labelKo: '녹스빌', lat: 35.96528, lon: -83.91978 },
  sunset:   { d1: '7:45 PM', d2: '7:44 PM' },
  twilight: { d1: '8:09 PM', d2: '8:08 PM' }
};

var LODGING = {
  name:    'Family-Friendly Chalet in the Smoky Mountains',
  nameKo:  '스모키 마운틴 샬레',
  host:    'Iuliia',
  /* Street number deliberately omitted: this site is published at a
     public URL. Directions are unaffected -- every Navigate link and
     map marker is built from the coordinates below, never the address
     string. Add the number back only if you keep the site private. */
  address: 'Summit Drive, Maggie Valley, NC',
  lat: 35.50643, lon: -83.06192,
  checkIn:  'Sat Sep 12, after 3:00 PM',
  checkInKo: '9월 12일 토요일 오후 3시 이후',
  checkOut: 'Sun Sep 13, by 11:00 AM',
  checkOutKo: '9월 13일 일요일 오전 11시까지',
  /* Summit Dr climbs ~350 ft above the valley floor on switchbacks:
     2.8 road miles from the club despite being 1.2 as the crow flies. */
  note:   'Steep switchbacked climb. Take it slowly after dark.',
  noteKo: '가파른 산길입니다. 어두워진 뒤에는 천천히 운전하세요.'
};

var COURSES = {
  maggie: {
    id: 'maggie',
    name: 'Maggie Valley Club & Resort',
    nameKo: '매기 밸리 클럽 & 리조트',
    address: '1819 Country Club Dr, Maggie Valley, NC 28751',
    phone: '(828) 926-6013',
    lat: 35.52258, lon: -83.04821,
    par: 72,
    architect: 'William Prevost Sr.',
    opened: 'early 1960s',          /* sources say 1961, 1962 and 1963 */
    greens: 'Bentgrass',
    fairways: 'Bluegrass',
    elevation: '~3,000 ft',
    dress:   'Collared shirts. No denim, no cargo pants or shorts.',
    dressKo: '카라 있는 셔츠 착용. 청바지와 카고 팬츠는 금지입니다.',
    dining: 'Pin High Bar & Grille',
    teeTimes: [
      { time: '12:10 PM', confirmed: true  },
      { time: '12:20 PM', confirmed: false }   /* inferred +10 min — CONFIRM */
    ],
    /* Par verified against the GolfLink scorecard: 36 out, 36 in. */
    parByHole:   [4,4,4,5,4,5,3,4,3, 4,4,3,5,4,3,4,4,5],
    /* PLACEHOLDER. Stroke index silently changes every net score —
       copy the real one off the card at the first tee. */
    strokeIndex: [1,2,3,4,5,6,7,8,9, 10,11,12,13,14,15,16,17,18],
    strokeIndexConfirmed: false,
    tees: {
      blue:  { name:'Blue',  yards:6466, cr:69.9, slope:128, verified:true  },
      white: { name:'White', yards:6130, cr:68.6, slope:125, verified:true  },
      gold:  { name:'Gold',  yards:5242, cr:70.5, slope:123, verified:false },
      green: { name:'Green', yards:4600, cr:67.0, slope:115, verified:false }
    }
  },

  sequoyah: {
    id: 'sequoyah',
    name: 'Sequoyah National Golf Club',
    nameKo: '세쿼이아 내셔널 골프클럽',
    address: '79 Cahons Rd, Whittier, NC 28789',
    phone: '(828) 497-3000',
    lat: 35.43208, lon: -83.33605,
    par: 72,
    architect: 'Robert Trent Jones II, with Notah Begay III',
    opened: 2009,
    greens: 'Bentgrass',
    fairways: 'Zeon zoysia',
    elevation: '~2,000-2,500 ft',
    dress:   'Collared shirts. Soft spikes only, metal spikes prohibited.',
    dressKo: '카라 있는 셔츠 착용. 소프트 스파이크만 허용됩니다.',
    dining: 'Sequoyah Grille',
    teeTimes: [
      { time: '2:30 PM', confirmed: true  },
      { time: '2:40 PM', confirmed: false }    /* inferred +10 min — CONFIRM */
    ],
    /* Five par-5s, five par-3s, eight par-4s: an unusual routing,
       and this array matches that distribution exactly. */
    parByHole:   [5,3,5,4,4,3,4,3,5, 4,5,5,3,4,4,4,3,4],
    /* PLACEHOLDER except hole 6, which is confirmed as stroke index 1. */
    strokeIndex: [7,15,11,13,9,1,5,17,3, 8,12,10,16,6,2,14,18,4],
    strokeIndexConfirmed: false,
    tees: {
      black:  { name:'Black',  yards:6517, cr:71.3, slope:143, verified:true },
      gold:   { name:'Gold',   yards:6135, cr:69.7, slope:140, verified:true },
      silver: { name:'Silver', yards:5691, cr:67.5, slope:130, verified:true },
      bronze: { name:'Bronze', yards:5235, cr:65.4, slope:118, verified:true,
                note:"appears to be a men's rating set" },
      jade:   { name:'Jade',   yards:4572, cr:63.8, slope:112, verified:true,
                note:"appears to be a men's rating set" }
    }
  }
};

/* Korean names are ROMANISATION GUESSES made from the English
   surnames. Correct them here: they are used everywhere a name
   appears on the site. */
var PLAYERS = [
  { id:'soh',  name:'Dr. Soh',  nameKo:'소 선생님', hi:12, team:'laurel',
    tees:{ maggie:'white', sequoyah:'gold'   } },
  { id:'jeon', name:'Dr. Jeon', nameKo:'전 선생님', hi:18, team:'laurel',
    tees:{ maggie:'white', sequoyah:'gold'   } },
  { id:'kang', name:'Dr. Kang', nameKo:'강 선생님', hi:24, team:'laurel',
    tees:{ maggie:'gold',  sequoyah:'bronze' } },
  { id:'oh',   name:'Dr. Oh',   nameKo:'오 선생님', hi:18, team:'balsam',
    tees:{ maggie:'white', sequoyah:'gold'   } },
  { id:'jo',   name:'Dr. Jo',   nameKo:'조 선생님', hi:20, team:'balsam',
    tees:{ maggie:'gold',  sequoyah:'bronze' } },
  { id:'kwon', name:'Dr. Kwon', nameKo:'권 선생님', hi:18, team:'balsam',
    tees:{ maggie:'gold',  sequoyah:'bronze' } }
];

/* Indexes total 110 and all six are even, so a 55/55 split is
   arithmetically impossible: 54/56 is the true optimum. This split
   balances PLAYING handicap to within 2 on each day and lands dead
   even, 98-98, across the full 36 holes. */
var TEAMS = {
  laurel: { id:'laurel', name:'Team Laurel', nameKo:'로럴 팀', accent:'var(--gold)'   },
  balsam: { id:'balsam', name:'Team Balsam', nameKo:'발삼 팀', accent:'var(--azalea)' }
};

/* ---- Format proposals -------------------------------------
   Nothing here is decided. These are options to argue about.
   EVERY ONE of them has you playing your own ball and keeping
   your own card -- that rules out a scramble, deliberately,
   because on courses this good you want your own score.
   All of these are two teams of three.                        */
var FORMATS = [
  { id:'best2', pick:'Best two of three',      pickKo:'상위 두 명',
    blurb:'Add up your team\'s two best net scores on each hole. Low team score wins the hole.',
    blurbKo:'매 홀 팀에서 잘 친 두 명의 네트 스코어를 더합니다. 낮은 팀이 그 홀을 가져갑니다.',
    good:'One blow-up hole costs you nothing, so nobody plays scared.',
    goodKo:'한 홀 크게 망쳐도 손해가 없어서 아무도 위축되지 않습니다.',
    recommended:true },

  { id:'all3', pick:'All three count',         pickKo:'세 명 모두 합산',
    blurb:'Every net score counts, every hole. Straight and merciless.',
    blurbKo:'매 홀 세 명의 네트 스코어를 모두 더합니다. 단순하고 냉정합니다.',
    good:'Simplest to score. But one bad hole really hurts.',
    goodKo:'계산이 가장 쉽습니다. 다만 한 홀만 망쳐도 크게 흔들립니다.' },

  { id:'stableford', pick:'Stableford points', pickKo:'스테이블포드',
    blurb:'Points per hole against your net par: birdie 4, par 2, bogey 1. Team adds them up.',
    blurbKo:'네트 파 기준으로 홀마다 점수를 매깁니다. 버디 4점, 파 2점, 보기 1점. 팀 합산.',
    good:'A wipe just scores zero and you move on. Fastest for pace of play.',
    goodKo:'크게 망친 홀은 0점으로 끝내고 넘어갑니다. 진행이 가장 빠릅니다.' }
];

/* ---- Waypoints for the illustrated map -------------------- */
var WAYPOINTS = [
  { name:'Knoxville', nameKo:'녹스빌', lat:35.96528, lon:-83.91978, kind:'city' },
  { name:'Pigeon River Gorge', nameKo:'피전 리버 협곡', lat:35.76000, lon:-83.10000, kind:'note',
    hook:'Where Helene tore the interstate off the mountainside.' },
  { name:'Max Patch', nameKo:'맥스 패치', lat:35.79500, lon:-82.96000, kind:'peak', ft:4629 },
  { name:'Cataloochee', nameKo:'카탈루치', lat:35.63000, lon:-83.10000, kind:'note',
    hook:'Elk herd and 1900s churches at the end of a gravel road.' },
  { name:'Waynesville', nameKo:'웨인스빌', lat:35.48870, lon:-82.98870, kind:'town' },
  { name:'Maggie Valley', nameKo:'매기 밸리', lat:35.51600, lon:-83.10020, kind:'town' },
  { name:'Soco Gap', nameKo:'소코 갭', lat:35.51800, lon:-83.19500, kind:'peak', ft:4340 },
  { name:'Soco Falls', nameKo:'소코 폭포', lat:35.49900, lon:-83.22600, kind:'note',
    hook:'Twin waterfall a short steep scramble off US-19.' },
  { name:'Waterrock Knob', nameKo:'워터록 노브', lat:35.45700, lon:-83.13800, kind:'peak', ft:5820 },
  { name:'Cherokee', nameKo:'체로키', lat:35.47400, lon:-83.31500, kind:'town' },
  { name:'Newfound Gap', nameKo:'뉴파운드 갭', lat:35.61100, lon:-83.42490, kind:'peak', ft:5046 },
  { name:'Kuwohi', nameKo:'쿠워히', lat:35.56280, lon:-83.49850, kind:'peak', ft:6643,
    hook:'Highest point in the park. Renamed from Clingmans Dome in 2024.' }
];

/* ---- Route legs -------------------------------------------
   Geometry was fetched ONCE from the public OSRM router and is
   frozen here, so the map has zero runtime dependency and works
   offline. Times are free-flow: they carry NO traffic and NO
   allowance for the single-lane gorge. */
var ROUTE = {
  knox_mvc: {
    from:'Knoxville, TN', to:'Maggie Valley Club',
    fromKo:'녹스빌', toKo:'매기 밸리 클럽',
    miles:91.8, minutes:115, day:1,
    via:'I-40 E through the Pigeon River Gorge, Exit 20 (US-276 S), US-19',
    viaKo:'I-40 동쪽 — 피전 리버 협곡, 20번 출구, US-19',
    geom:[[35.9651,-83.9202],[35.9696,-83.9155],[35.984,-83.9154],[36.0135,-83.8592],[36.0072,-83.8343],[36.0094,-83.8203],[36.0029,-83.783],[36.0047,-83.7463],[35.9974,-83.7216],[35.9957,-83.6846],[35.9821,-83.6168],[35.9861,-83.5849],[36.0111,-83.5206],[36.0257,-83.4661],[36.067,-83.3888],[36.0507,-83.3518],[36.0221,-83.2999],[35.988,-83.2832],[35.9735,-83.2696],[35.967,-83.2449],[35.9682,-83.2269],[35.9557,-83.2071],[35.9276,-83.191],[35.9033,-83.1842],[35.8854,-83.1878],[35.8254,-83.1835],[35.8127,-83.1766],[35.8212,-83.154],[35.8196,-83.1456],[35.7967,-83.1299],[35.7966,-83.1161],[35.7811,-83.1087],[35.7705,-83.0826],[35.7506,-83.0649],[35.7574,-83.052],[35.7549,-83.0334],[35.741,-83.0361],[35.7383,-83.0245],[35.7282,-83.0231],[35.7206,-83.0385],[35.7048,-83.0294],[35.6973,-83.0454],[35.6869,-83.0305],[35.6758,-83.0244],[35.6658,-82.9911],[35.6459,-82.9969],[35.6368,-82.9899],[35.6265,-83.008],[35.6157,-83.0121],[35.6006,-83.0069],[35.561,-83.0219],[35.5222,-83.0283],[35.5229,-83.0482]]
  },
  mvc_chalet: {
    from:'Maggie Valley Club', to:'the chalet',
    fromKo:'매기 밸리 클럽', toKo:'샬레',
    miles:2.8, minutes:8, day:1,
    via:'Country Club Dr, then the switchbacks up Summit Dr',
    viaKo:'컨트리클럽 드라이브에서 서밋 드라이브 산길로',
    geom:[[35.5229,-83.0482],[35.5231,-83.0487],[35.5227,-83.0489],[35.5215,-83.0483],[35.5209,-83.0471],[35.5206,-83.0468],[35.5207,-83.0461],[35.5208,-83.0398],[35.5206,-83.0395],[35.5204,-83.0403],[35.5199,-83.0405],[35.516,-83.0605],[35.5154,-83.0623],[35.5122,-83.0616],[35.5107,-83.0619],[35.5078,-83.0633],[35.5073,-83.0634],[35.5071,-83.0627],[35.5077,-83.0615],[35.5073,-83.0619],[35.5064,-83.062]]
  },
  chalet_seq: {
    from:'the chalet', to:'Sequoyah National',
    fromKo:'샬레', toKo:'세쿼이아 내셔널',
    miles:23.1, minutes:44, day:2,
    via:'US-19 W over Soco Gap, through Cherokee',
    viaKo:'US-19 서쪽 — 소코 갭을 넘어 체로키 경유',
    geom:[[35.5064,-83.062],[35.5073,-83.0619],[35.5064,-83.0645],[35.5143,-83.0656],[35.5121,-83.072],[35.5121,-83.0767],[35.5172,-83.0884],[35.5184,-83.1026],[35.5233,-83.1148],[35.5203,-83.1225],[35.513,-83.1308],[35.5125,-83.136],[35.5094,-83.1419],[35.501,-83.1484],[35.4995,-83.1526],[35.4918,-83.1605],[35.4906,-83.1658],[35.4962,-83.1687],[35.493,-83.1695],[35.4917,-83.175],[35.4923,-83.1795],[35.491,-83.1812],[35.4932,-83.1884],[35.4906,-83.1911],[35.4867,-83.1918],[35.4865,-83.1958],[35.4847,-83.1961],[35.4833,-83.1993],[35.4792,-83.2018],[35.4784,-83.2114],[35.4764,-83.2146],[35.4741,-83.2133],[35.4717,-83.2146],[35.4731,-83.2193],[35.472,-83.2256],[35.4684,-83.232],[35.4653,-83.2343],[35.4652,-83.2396],[35.4701,-83.2426],[35.4713,-83.2454],[35.4669,-83.2707],[35.4693,-83.2882],[35.4684,-83.2996],[35.4694,-83.3052],[35.4643,-83.3099],[35.461,-83.3153],[35.4515,-83.3075],[35.4471,-83.308],[35.4447,-83.3122],[35.4442,-83.3176],[35.4381,-83.3252],[35.4273,-83.3259],[35.4233,-83.3308],[35.4221,-83.3352],[35.4229,-83.3379],[35.4289,-83.3385]]
  },
  seq_knox_441: {
    from:'Sequoyah National', to:'Knoxville, TN',
    fromKo:'세쿼이아 내셔널', toKo:'녹스빌',
    miles:83.2, minutes:143, day:2, option:'scenic',
    via:'US-441 over Newfound Gap, through Gatlinburg',
    viaKo:'US-441 — 뉴파운드 갭을 넘어 개틀린버그 경유',
    geom:[[35.4289,-83.3385],[35.4229,-83.3379],[35.4233,-83.3308],[35.4381,-83.3252],[35.4479,-83.3074],[35.4754,-83.3286],[35.4765,-83.3192],[35.5,-83.306],[35.5014,-83.2992],[35.5212,-83.3081],[35.5416,-83.299],[35.5546,-83.3107],[35.5642,-83.333],[35.5806,-83.3465],[35.6029,-83.415],[35.588,-83.3974],[35.5864,-83.4041],[35.6068,-83.4359],[35.6111,-83.425],[35.6251,-83.4183],[35.6185,-83.4313],[35.631,-83.4603],[35.6375,-83.4644],[35.6347,-83.4668],[35.6411,-83.4813],[35.6386,-83.4921],[35.6418,-83.4978],[35.6368,-83.4939],[35.64,-83.5036],[35.6643,-83.5273],[35.6746,-83.5264],[35.6863,-83.5361],[35.7028,-83.5287],[35.71,-83.5337],[35.7131,-83.5276],[35.7157,-83.5334],[35.7241,-83.5145],[35.7384,-83.5225],[35.7429,-83.5178],[35.7567,-83.5206],[35.7695,-83.5274],[35.7771,-83.545],[35.8071,-83.5774],[35.8211,-83.578],[35.8608,-83.5656],[35.8713,-83.5674],[35.892,-83.5806],[35.9467,-83.5844],[35.9846,-83.6087],[35.9831,-83.6279],[36.005,-83.7466],[36.0032,-83.7827],[36.0096,-83.8197],[36.0072,-83.834],[36.0137,-83.8583],[35.984,-83.9181],[35.9697,-83.9157],[35.9651,-83.9202]]
  },
  seq_knox_i40: {
    from:'Sequoyah National', to:'Knoxville, TN',
    fromKo:'세쿼이아 내셔널', toKo:'녹스빌',
    miles:126.8, minutes:181, day:2, option:'interstate',
    via:'US-74 E, then I-40 W through the gorge',
    viaKo:'US-74 동쪽에서 I-40 서쪽 — 협곡 통과',
    geom:[[35.4289,-83.3385],[35.4043,-83.3206],[35.4052,-83.2935],[35.3942,-83.2979],[35.3803,-83.2844],[35.3884,-83.2707],[35.3803,-83.2643],[35.3747,-83.2393],[35.3962,-83.2041],[35.3913,-83.185],[35.3925,-83.146],[35.3975,-83.1266],[35.4238,-83.1098],[35.4326,-83.095],[35.4319,-83.0812],[35.4509,-83.0611],[35.4554,-83.0501],[35.4608,-83.0146],[35.4825,-83.0101],[35.5031,-82.9964],[35.5222,-82.957],[35.5319,-82.9607],[35.5572,-82.9518],[35.579,-82.9701],[35.594,-82.9685],[35.6003,-82.9801],[35.594,-82.9685],[35.6102,-82.9696],[35.6125,-82.9655],[35.6215,-82.9699],[35.6232,-82.9826],[35.6308,-82.9872],[35.6413,-82.979],[35.6563,-82.9787],[35.6697,-82.9937],[35.6759,-83.0243],[35.6869,-83.0304],[35.6973,-83.0453],[35.7048,-83.0292],[35.7205,-83.0376],[35.7282,-83.0229],[35.7383,-83.0244],[35.7413,-83.0361],[35.7551,-83.0333],[35.7575,-83.0522],[35.7505,-83.0645],[35.7708,-83.0829],[35.7812,-83.1087],[35.7966,-83.1159],[35.7965,-83.1296],[35.8195,-83.1451],[35.8213,-83.154],[35.8121,-83.1748],[35.819,-83.1807],[35.8845,-83.1875],[35.9033,-83.1839],[35.9269,-83.1904],[35.9567,-83.2075],[35.9684,-83.2268],[35.9671,-83.244],[35.9737,-83.2695],[35.9881,-83.283],[36.0233,-83.301],[36.0674,-83.3838],[36.0258,-83.4663],[36.011,-83.5221],[35.9859,-83.5882],[35.9827,-83.625],[36.005,-83.7466],[36.0032,-83.7827],[36.0096,-83.8197],[36.0072,-83.834],[36.0137,-83.8583],[35.984,-83.9181],[35.9697,-83.9157],[35.9651,-83.9202]]
  }
};

/* ============================================================
   SCORES — THE ONLY BLOCK YOU EDIT DURING THE TRIP
   18 gross strokes per player, holes 1 through 18.
   Leave null for holes not yet played: a partial round scores
   correctly, and only completed holes count.
   ============================================================ */
var N = null;
var SCORES = {
  maggie: {
    soh:  [N,N,N,N,N,N,N,N,N, N,N,N,N,N,N,N,N,N],
    jeon: [N,N,N,N,N,N,N,N,N, N,N,N,N,N,N,N,N,N],
    kang: [N,N,N,N,N,N,N,N,N, N,N,N,N,N,N,N,N,N],
    oh:   [N,N,N,N,N,N,N,N,N, N,N,N,N,N,N,N,N,N],
    jo:   [N,N,N,N,N,N,N,N,N, N,N,N,N,N,N,N,N,N],
    kwon: [N,N,N,N,N,N,N,N,N, N,N,N,N,N,N,N,N,N]
  },
  sequoyah: {
    soh:  [N,N,N,N,N,N,N,N,N, N,N,N,N,N,N,N,N,N],
    jeon: [N,N,N,N,N,N,N,N,N, N,N,N,N,N,N,N,N,N],
    kang: [N,N,N,N,N,N,N,N,N, N,N,N,N,N,N,N,N,N],
    oh:   [N,N,N,N,N,N,N,N,N, N,N,N,N,N,N,N,N,N],
    jo:   [N,N,N,N,N,N,N,N,N, N,N,N,N,N,N,N,N,N],
    kwon: [N,N,N,N,N,N,N,N,N, N,N,N,N,N,N,N,N,N]
  }
};

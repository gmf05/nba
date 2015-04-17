% parsePossession.m
% Grant Fiddyment, Boston University, 2015/03/06
%
% matlab script to parse ball possession based on NBA play-by-play data
% Note: assumes play-by-play is already encoded as point process data 
%
% TODO:
% -for clear path fouls, stop & re-start possession??
% 
%


% load event data
team = 'ATL';
load(['stats_201415_' team '.mat']); % encoded via nbastats.py

% initialize arrays
list = [];
Ngames = length(games);
% games = reshape(games,[],Ngames)'; % fix game list if shaped wrong
sumSec = [0 cumsum(secPerGame)];
Nsec = sumSec(end);
winSize = 12; % max time to wait for rebounds
rebs0 = zeros(2,Nsec); % split offensive & defensive
orebs0 = zeros(2,Nsec); % split opponent's rebounds into offensive & defensive
possStart = zeros(1,Nsec); % start-possession times for team of interest
possStop = zeros(1,Nsec); % stop-possession times for team of interest
opossStart = zeros(1,Nsec); % start-possession times for opponent
opossStop = zeros(1,Nsec); % stop-possession times for opponent
shotchange = zeros(2,Nsec); % shot (1) -> defensive rebound (2) sequences
oshotchange = zeros(2,Nsec); % shot (1) -> defensive rebound (2) sequences

% get time indices for some relevant events
finalfts(1,:) = (finalfts(1,:)>0);
finalofts(1,:) = (finalofts(1,:)>0);
attempts = shots(1,:) + shots(3,:) + fts(1,:);
oattempts = oshots(1,:) + oshots(3,:) + ofts(1,:);
% NOTE: we only include FTs in makes & misses if they are *FINAL* FTs
misses = shots(1,:) - shots(2,:) + shots(3,:) - shots(4,:) + finalfts(1,:) - finalfts(2,:);
omisses = oshots(1,:) - oshots(2,:) + oshots(3,:) - oshots(4,:) + finalofts(1,:) - finalofts(2,:);
missind = find(misses);
omissind = find(omisses);
fgmade = shots(2,:) + shots(4,:) - ofouls; % do this in two stages to handle and-1
fgmade(fgmade<0) = 0; fgmade = fgmade + finalfts(2,:);
madeind = find(fgmade);
ofgmade = oshots(2,:) + oshots(4,:) - fouls; % do this in two stages to handle and-1
ofgmade(ofgmade<0) = 0; ofgmade = ofgmade + finalofts(2,:);
omadeind = find(ofgmade);
% madeind = find(shots(2,:) + shots(4,:) + finalfts(2,:));
% omadeind = find(oshots(2,:) + oshots(4,:) + finalofts(2,:));
toind = find(tos);
otoind = find(otos);

% make list of quarter start/stop times
i = 1;
secPerQtr = zeros(2, 5*Ngames);
qtrsPerGame = zeros(1,Ngames);
for game = 1:Ngames
    secPerQtr(1,i:i+3) = 720;
    secPerQtr(2,i:i+3) = game;
    i = i+4;
    NOT = 0;
    if secPerGame(game)>2880 % is there overtime?
        % each overtime is 300 sec
        NOT = (secPerGame(game) - 2880) / 300;
        secPerQtr(1,i:i+NOT-1) = 300;
        secPerQtr(2,i:i+NOT-1) = game;
        i = i+NOT;
    end
    qtrsPerGame(game) = 4 + NOT;
end
secPerQtr(:,i:end)=[];
sumSecQtr = [0 cumsum(secPerQtr(1,:))];
Nqtrs = length(secPerQtr);

% drop end of quarters from event lists since they are handled separately
for i = 1:Nqtrs
    toind(toind==sumSecQtr(i+1))=[];
    madeind(madeind==sumSecQtr(i+1))=[];
    missind(missind==sumSecQtr(i+1))=[];
    otoind(otoind==sumSecQtr(i+1))=[];
    omadeind(omadeind==sumSecQtr(i+1))=[];
    omissind(omissind==sumSecQtr(i+1))=[];
end

% Separate offensive & defensive rebounds for team:
% for each miss, find rebound
qtrind = 1;
for i = missind  
  % how much time is left in quarter?
  % only consider events up to end of qtr
  while sumSecQtr(qtrind) < i, qtrind = qtrind+1; end
  i0 = min(i+winSize, sumSecQtr(qtrind));

  % which team rebounds this miss?
  j1 = find(rebs(i:i0),1,'first'); if isempty(j1), j1=Inf; end
  j2 = find(orebs(i:i0),1,'first'); if isempty(j2), j2=Inf; end
%   j1 = find(rebs(i+1:i0),1,'first'); if isempty(j1), j1=Inf; end
%   j2 = find(orebs(i+1:i0),1,'first'); if isempty(j2), j2=Inf; end

  % in the unique case that offensive rebound -> foul -> missed free throw -> rebound
  % cycle happens within a second, skip from offensive rebound to next rebound
  if j1==1 && j2<Inf && ofouls(i) && finalfts(1,i) && (finalfts(2,i) < finalfts(1,i))
    j1 = find(rebs(i+1:i0),1,'first'); if isempty(j1), j1=Inf; else j1=j1+1; end
    list = [list i];
%     i % debug
%     [gind,nQtr,nMin,nSec] = gamesElapsed(i, secPerGame); % debug
%     fprintf('Simultaneous events: foul, free throw, rebound\n'); % debug
%     fprintf([ games(gind,:) ' Q' num2str(nQtr) ' ' num2str(12-nMin) ':' num2str(60-nSec) '\n']); % debug
  end

  if j1<j2 % team is first: offensive rebound
    rebs0(1,i-1+j1) = 1;
  elseif j2<=j1 && j2<Inf % defensive rebound
    orebs0(2,i-1+j2) = 1;
    oshotchange(1,i) = 1;
    oshotchange(2,i-1+j2) = 2;    
  elseif j1==Inf && j2==Inf % no rebound
    % debugging
    list = [list i];
    i
    [gind,nQtr,nMin,nSec] = gamesElapsed(i, secPerGame);
    fprintf('No rebound?\n');
    fprintf([ games(gind,:) ' Q' num2str(nQtr) ' ' num2str(12-nMin) ':' num2str(60-nSec) '\n']);
%       shotchange(1,i) = 1;
  end
end

% Separate offensive & defensive rebounds for opponent
qtrind = 1;
for i = omissind  
  % what is time at upcoming end of qtr?
  while sumSecQtr(qtrind) < i, qtrind = qtrind+1; end
  i0 = min(i+winSize, sumSecQtr(qtrind));

  % which team rebounds this miss?
  j1 = find(rebs(i:i0),1,'first'); if isempty(j1), j1=Inf; end
  j2 = find(orebs(i:i0),1,'first'); if isempty(j2), j2=Inf; end
%   j1 = find(rebs(i+1:i0),1,'first'); if isempty(j1), j1=Inf; end
%   j2 = find(orebs(i+1:i0),1,'first'); if isempty(j2), j2=Inf; end

  % in the unique case that offensive rebound -> foul -> missed free throw -> rebound
  % cycle happens within a second, skip from offensive rebound to next rebound
  if j2==1 && j1<Inf && fouls(i) && finalofts(1,i) && (finalofts(2,i) < finalofts(1,i))
    j2 = find(orebs(i+1:i0),1,'first'); if isempty(j2), j2=Inf; else j2=j2+1; end
    % debugging
    list = [list i];
%     i
%     [gind,nQtr,nMin,nSec] = gamesElapsed(i, secPerGame);
%     fprintf('Simultaneous events: foul, free throw, rebound\n');
%     fprintf([ games(gind,:) ' Q' num2str(nQtr) ' ' num2str(12-nMin) ':' num2str(60-nSec) '\n']);
  end

  if j2<j1 % opponent is first: offensive rebound
    orebs0(1,i-1+j2) = 1;
  elseif j1<=j2 && j1<Inf % defensive rebound
    rebs0(2,i-1+j1) = 1;
    shotchange(1,i) = 1;
    shotchange(2,i-1+j1) = 2;
  elseif j1==Inf && j2==Inf % no rebound
    % debugging
    i
    list = [list i];
    [gind,nQtr,nMin,nSec] = gamesElapsed(i, secPerGame);
    fprintf('No rebound?\n');
    fprintf([ games(gind,:) ' Q' num2str(nQtr) ' ' num2str(12-nMin) ':' num2str(60-nSec) '\n']);
%       oshotchange(1,i) = 1;
  end
end

% drop end of quarters from event lists since they are handled separately
shotchange(:,sumSecQtr(2:end)) = 0;
oshotchange(:,sumSecQtr(2:end)) = 0;

% for plays in between...
% stop & re-start possession for every
% 1. turnover
possStop(toind) = 1;
opossStart(toind) = 1;
possStart(otoind) = 1;
opossStop(otoind) = 1;

% 2. made shot (including free throws)
possStop(madeind) = 1;
opossStart(madeind) = 1;
opossStop(omadeind) = 1;
possStart(omadeind) = 1;

% 3. missed shot -> defensive rebound
opossStop(shotchange(1,:)==1) = 1;
possStart(rebs0(2,:)==1) = 1;
possStop(oshotchange(1,:)==1) = 1;
opossStart(oshotchange(2,:)==2) = 1;
opossStart(orebs0(2,:)==1) = 1;

% handle possession start & stop at quarter beginning/end
for i = 1:Nqtrs
    game = secPerQtr(2,i);
    % opp is either 9:11 or 12:14
    if isequal(games(game,9:11),team)
      opp = games(game,12:14);
    else
      opp = games(game,9:11);
    end

    % start-possession at beginning
    qtrT = sumSecQtr(i)+1:sumSecQtr(i+1);    
    firstTeamEvent = find(possStop(qtrT),1,'first');
    firstOppEvent = find(opossStop(qtrT),1,'first');

    if firstTeamEvent < firstOppEvent
%         ind = find(secPerQtr(2,:)==game); % debug
%         gameQtr = find(ind==i); % debug
%         fprintf([games(game,:) ' Game #' num2str(game) ' Qtr ' num2str(gameQtr) ': ' team ' ball\n']); % debug
        possStart(sumSecQtr(i)+1) = 1;
    else
%         ind = find(secPerQtr(2,:)==game); % debug
%         gameQtr = find(ind==i); % debug
%         fprintf([games(game,:) ' Game #' num2str(game) ' Qtr ' num2str(gameQtr) ': ' opp ' ball\n']); % debug
        opossStart(sumSecQtr(i)+1) = 1;
    end

    % stop-possession at end
    qtrT = sumSecQtr(i)+1:sumSecQtr(i+1);    
    lastTeamEvent = find(possStart(qtrT),1,'last');
    lastOppEvent = find(opossStart(qtrT),1,'last');
    if lastTeamEvent > lastOppEvent
%         ind = find(secPerQtr(2,:)==game); % debug
%         gameQtr = find(ind==i); % debug
%         fprintf([games(game,:) ' Game #' num2str(game) ' End Qtr ' num2str(gameQtr) ': ' team ' ball\n']); % debug
        possStop(sumSecQtr(i+1)) = 1;
    else
%         ind = find(secPerQtr(2,:)==game); % debug
%         gameQtr = find(ind==i); % debug
%         fprintf([games(game,:) ' Game #' num2str(game) ' End Qtr ' num2str(gameQtr) ': ' opp ' ball\n']); % debug
        opossStop(sumSecQtr(i+1)) = 1;
    end
end
%%%%%%%%%%%%%%

% % %%% 5a. finally test and
% % % make sure all start/stop come in pairs
% % % TODO: Make sure this works!
% % % Obviously it doesn't since numbers sometimes come out negative!!!
% % tStart = find(possStart,1,'first');
% % prevStart0 = 0;
% % prevStart1 = tStart;
% % prevStop = 0;
% % isStarted = 1;
% % for t = tStart+1:Nsec   
% %   if possStart(t) && isStarted
% % %     [prevStart0, prevStart1, t]
% %     possStart(prevStart0) = 0;
% %     prevStart0 = prevStart1;
% %     prevStart1 = t;
% %     isStarted = 1;
% %   elseif possStart(t)
% %     prevStart0 = prevStart1;
% %     prevStart1 = t;
% %     isStarted = 1;
% %   end
% % 
% %   if possStop(t)
% %     if isStarted
% %       isStarted = 0;
% %       prevStop = t;
% %     else
% %       possStop(t) = 0;
% % %       error('asdf')
% %     end
% %   end
% % end
% % % 5b. repeat for opponent
% % tStart = find(opossStart,1,'first');
% % prevStart0 = 0;
% % prevStart1 = tStart;
% % prevStop = 0;
% % isStarted = 1;
% % for t = tStart+1:Nsec 
% %   if opossStart(t) && isStarted
% % %     [prevStart0, prevStart1, t]
% %     opossStart(prevStart0) = 0;
% %     prevStart0 = prevStart1;
% %     prevStart1 = t;
% %     isStarted = 1;
% %   elseif opossStart(t)
% %     prevStart0 = prevStart1;
% %     prevStart1 = t;
% %     isStarted = 1;
% %   end
% % 
% %   if opossStop(t)
% %     if isStarted
% %       isStarted = 0;
% %       prevStop = t;
% %     else
% %       opossStop(t) = 0;
% % %       error('asdf')
% %     end
% %   end
% % end

% %%
% debug
% length(find(tos + oreb0(2,:) + shots(2,:) + shots(4,:)))
% length(find(tos + shots(2,:) + shots(4,:)))
% [sum(possStart) sum(possStop)]
% length(find(otos + oreb0(2,:) + oshots(2,:) + oshots(4,:)))
% length(find(otos + oshots(2,:) + oshots(4,:)))
% [sum(opossStart) sum(opossStop)]


[sum(possStart) sum(possStop) sum(opossStart) sum(opossStop)]

%%
figure
plot(possStart+1,'b','linewidth',2); hold on;
plot(possStop,'r','linewidth',2);

plot(opossStart,'b'); hold on;
plot(opossStop+1,'r');


%% % scroll through
N = 30;
xlim([0,N]); pause;
for n = 1:50, xlim(get(gca,'XLim')+N), pause, end

% % look at beg/end of quarters
% for i = 1:Nqtrs
%   ylim([0,2]);
%   xlim(sumSecQtr(i) + 35*[-1,1]); pause;
% end


%% histogram of possession times
startind = find(possStart);
stopind = find(possStop);
N = length(startind);
possLength = zeros(1,N);
for n = 1:N
  possLength(n) = stopind(n) - startind(n);
end

p0 = possLength; p0(p0<0) = []; hist(p0,0:200)

%% debug: print possession outcomes in order

Nstart = sum(possStart);
Nstop = sum(possStop);
times = [[find(possStart); ones(1,Nstart)] [find(possStop); 2*ones(1,Nstop)]];
[~,sortind] = sort(times(1,:));
times = times(:,sortind);

times(:,times(1,:)>2880) = [];

for i = 1:length(times)
  t = times(1,i);
  isStop = times(2,i) - 1;
  [game, qtr, mins, secs] = gamesElapsed(t, secPerGame);
  if ~isStop
    fprintf([games(game,:) ' G' num2str(game) ' Q' num2str(qtr) ' ' num2str(11-mins) ':' num2str(60-secs) ' Possession Start ']);
  else
    fprintf([games(game,:) ' G' num2str(game) ' Q' num2str(qtr) ' ' num2str(11-mins) ':' num2str(60-secs) ' Possession End ']);
  end
  
  if tos(t), fprintf(['Turnover ']); end
  if rebs(t), fprintf(['Rebound ']); end
  if shots(1,t), fprintf(['2pt attempt ']); end
  if shots(2,t), fprintf(['made']); end
  if shots(3,t), fprintf(['3pt attempt ']); end
  if shots(4,t), fprintf(['made']); end
  if any(finalfts(:,t)), fprintf(['Free throw ']); end
  
  if otos(t), fprintf(['Opp Turnover ']); end
  if orebs(t), fprintf(['Opp Rebound ']); end
  if oshots(1,t), fprintf(['Opp 2pt attempt ']); end
  if oshots(2,t), fprintf(['made']); end
  if oshots(3,t), fprintf(['Opp 3pt attempt ']); end
  if oshots(4,t), fprintf(['made']); end
  if any(finalofts(:,t)), fprintf(['Opp Free throw ']); end
  
  fprintf('\n');

end

%% look for start/start or stop/stop
% Need to handle And-1 situations:
% made shot does not guarantee possession re-starts for other team
%
% Also problem at 20141105ATLSAS Q4 02:05 left : Duncan rebound, tip miss, rebound, tip miss
% 
%

Nstart = sum(possStart);
Nstop = sum(possStop);
times = [[find(possStart); ones(1,Nstart)] [find(possStop); 2*ones(1,Nstop)]];
[~,sortind] = sort(times(1,:));
times = times(:,sortind);
ind = find(diff(times(2,:))==0);
% times(:, ind)

for i = 1:length(ind)
  t = times(1, ind(i));
  [game, qtr, mins, secs] = gamesElapsed(t, secPerGame);
  fprintf([games(game,:) ' G' num2str(game) ' Q' num2str(qtr) ' ' num2str(11-mins) ':' num2str(60-secs) '  ' num2str(t) '\n']);
end
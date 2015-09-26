% parsePossession.m
% Grant Fiddyment, Boston University, 2015/03/06
%
% matlab script to parse ball possession based on NBA play-by-play data
% Note: assumes play-by-play is already encoded as point process data 
%

% load event data
teams = {'ATL', 'BKN', 'BOS', 'CHA', 'CHI', 'CLE', 'DAL', ...
  'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', ...
  'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', ...
  'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS'};

% for t = teams(1)

  team = teams{1}; % ATL
  load(['stats_201415_' team '.mat']); % encoded via nbastats.py

  % initialize arrays
  Ngames = length(games);
  % games = reshape(games,[],Ngames)'; % fix game list if shaped wrong
  winSize = 12; % max time to wait for rebounds
  Nsec = sum(secPerGame);
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
  madeind = find(shots(2,:) + shots(4,:) + finalfts(2,:));
  omadeind = find(oshots(2,:) + oshots(4,:) + finalofts(2,:));
  toind = find(tos);
  otoind = find(otos);

  % make list of quarter start/stop times
  i = 1;
  secPerQtr = zeros(2, 5*Ngames);
  for game = 1:Ngames
      secPerQtr(1,i:i+3) = 720;
      secPerQtr(2,i:i+3) = game;
      i = i+4;
      if secPerGame(game)>2880 % is there overtime?
          % each overtime is 300 sec
          NOT = (secPerGame(game) - 2880) / 300;
          secPerQtr(1,i:i+NOT-1) = 300;
          secPerQtr(2,i:i+NOT-1) = game;
          i = i+NOT;
      end
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

  % First separate off & def rebounds:
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

    % in the unique case that offensive rebound -> foul -> missed free throw -> defensive rebound
    % cycle happens within a second, skip to defensive rebound
    if j1==1 && j2<Inf && ofouls(i) && finalfts(1,i) && (finalfts(2,i) < finalfts(1,i))
      j1 = Inf;
    end

    if j1<j2 % team is first: offensive rebound
      rebs0(1,i-1+j1) = 1;
    elseif j2<=j1 && j2<Inf % defensive rebound
      orebs0(2,i-1+j2) = 1;
      oshotchange(1,i) = 1;
      oshotchange(2,i-1+j2) = 2;    
    elseif j1==Inf && j2==Inf % no rebound
      i
      [sumSecQtr(find(sumSecQtr<i,1,'last'))/2880, i - sumSecQtr(find(sumSecQtr<i,1,'last')), (720 - (i - sumSecQtr(find(sumSecQtr<i,1,'last'))))/60] % ind, game #, time into quarter
%       shotchange(1,i) = 1;
    end
  end

  % repeat for opponent
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

    % in the unique case that offensive rebound -> foul -> missed free throw -> defensive rebound
    % cycle happens within a second, skip to defensive rebound
    if j2==1 && j1<Inf && fouls(i) && finalofts(1,i) && (finalofts(2,i) < finalofts(1,i))
      j2 = Inf;
    end

    if j2<j1 % opponent is first: offensive rebound
      orebs0(1,i-1+j2) = 1;
    elseif j1<=j2 && j1<Inf % defensive rebound
      rebs0(2,i-1+j1) = 1;
      shotchange(1,i) = 1;
      shotchange(2,i-1+j1) = 2;
    elseif j1==Inf && j2==Inf % no rebound
      i
      [sumSecQtr(find(sumSecQtr<i,1,'last'))/2880, i - sumSecQtr(find(sumSecQtr<i,1,'last')), (720 - (i - sumSecQtr(find(sumSecQtr<i,1,'last'))))/60] % ind, game #, time into quarter
%       oshotchange(1,i) = 1;
    end
  end

% drop end of quarters from event lists since they are handled separately
  shotchange(:,sumSecQtr(2:end)) = 0;
  oshotchange(:,sumSecQtr(2:end)) = 0;
  
  %%%%%%%%%%%%%%
  % TO DO: IMPROVE THIS
  % 1. handle start & stop-possession at ends of quarter
  for i = 1:Nqtrs
      game = secPerQtr(2,i);
      % opp is either 9:11 or 12:14
      if isequal(games(game,9:11),team)
        opp = games(game,12:14);
      else
        opp = games(game,9:11);
      end

      % start-possession at beginning
      teamEvents = attempts(sumSecQtr(i)+1:sumSecQtr(i+1)) + tos(sumSecQtr(i)+1:sumSecQtr(i+1)) + rebs(sumSecQtr(i)+1:sumSecQtr(i+1));
      oppEvents = oattempts(sumSecQtr(i)+1:sumSecQtr(i+1)) + otos(sumSecQtr(i)+1:sumSecQtr(i+1)) + orebs(sumSecQtr(i)+1:sumSecQtr(i+1));
      firstTeamEvent = find(teamEvents,1,'first');
      firstOppEvent = find(oppEvents,1,'first');
      if firstTeamEvent < firstOppEvent
  %         fprintf([games(game,:) ' Qtr ' num2str(i) ': ' team ' ball\n']); % debug
          possStart(sumSecQtr(i)+1) = 1;
      else
  %         fprintf([games(game,:) 'Qtr ' num2str(i) ': ' opp ' ball\n']); % debug
          opossStart(sumSecQtr(i)+1) = 1;
      end

      % stop-possession at end
      lastTeamEvent = find(teamEvents,1,'last');
      lastOppEvent = find(oppEvents,1,'last');
      if lastTeamEvent > lastOppEvent
  %         fprintf([games(game,:) ' End Qtr ' num2str(i) ': ' team ' ball\n']); % debug
          possStop(sumSecQtr(i+1)) = 1;
      else
  %         fprintf([games(game,:) 'End Qtr ' num2str(i) ': ' opp ' ball\n']); % debug
          opossStop(sumSecQtr(i+1)) = 1;
      end
  end
  %%%%%%%%%%%%%%
  
  
  % for plays in between...
  % stop & re-start possession for every
  % 2. turnover
  possStop(toind) = 1;
  opossStart(toind) = 1;
  possStart(otoind) = 1;
  opossStop(otoind) = 1;

  % 3. made shot (including free throws)
  possStop(madeind) = 1;
  opossStart(madeind) = 1;
  opossStop(omadeind) = 1;
  possStart(omadeind) = 1;

  % 4. missed shot -> defensive rebound
  opossStop(shotchange(1,:)==1) = 1;
  possStart(rebs0(2,:)==1) = 1;
  possStop(oshotchange(1,:)==1) = 1;
  opossStart(oshotchange(2,:)==2) = 1;
  opossStart(orebs0(2,:)==1) = 1;
   
% %   %% 5a. finally test and
% %   % make sure all start/stop come in pairs
% %   % TODO: Make sure this works!
% %   % Obviously it doesn't since numbers sometimes come out negative!!!
% %   tStart = find(possStart,1,'first');
% %   prevStart0 = 0;
% %   prevStart1 = tStart;
% %   prevStop = 0;
% %   isStarted = 1;
% %   for t = tStart+1:Nsec 
% %     if possStart(t) && isStarted
% %   %     [prevStart0, prevStart1, t]
% %       possStart(prevStart0) = 0;
% %       prevStart0 = prevStart1;
% %       prevStart1 = t;
% %       isStarted = 1;
% %     elseif possStart(t)
% %       prevStart0 = prevStart1;
% %       prevStart1 = t;
% %       isStarted = 1;
% %     end
% % 
% %     if possStop(t)
% %       if isStarted
% %         isStarted = 0;
% %         prevStop = t;
% %       else
% %         possStop(t) = 0;
% %   %       error('asdf')
% %       end
% %     end
% %   end
% %   % 5b. repeat for opponent
% %   tStart = find(opossStart,1,'first');
% %   prevStart0 = 0;
% %   prevStart1 = tStart;
% %   prevStop = 0;
% %   isStarted = 1;
% %   for t = tStart+1:Nsec 
% %     if opossStart(t) && isStarted
% %   %     [prevStart0, prevStart1, t]
% %       opossStart(prevStart0) = 0;
% %       prevStart0 = prevStart1;
% %       prevStart1 = t;
% %       isStarted = 1;
% %     elseif opossStart(t)
% %       prevStart0 = prevStart1;
% %       prevStart1 = t;
% %       isStarted = 1;
% %     end
% % 
% %     if opossStop(t)
% %       if isStarted
% %         isStarted = 0;
% %         prevStop = t;
% %       else
% %         opossStop(t) = 0;
% %   %       error('asdf')
% %       end
% %     end
% %   end

  % %%
  % debug
  % length(find(tos + oreb0(2,:) + shots(2,:) + shots(4,:)))
  % length(find(tos + shots(2,:) + shots(4,:)))
  % [sum(possStart) sum(possStop)]
  % length(find(otos + oreb0(2,:) + oshots(2,:) + oshots(4,:)))
  % length(find(otos + oshots(2,:) + oshots(4,:)))
  % [sum(opossStart) sum(opossStop)]

  [sum(possStart) sum(possStop) sum(opossStart) sum(opossStop)]
%   pause

% end

%%
figure
plot(possStart+1,'b'); hold on;
plot(possStop,'r');

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

%% debug start/stop
% 5a. finally test and
% make sure all start/stop come in pairs
% TODO: Make sure this works!
% Obviously it doesn't since numbers sometimes come out negative!!!

 
tStart = find(possStart,1,'first');
prevStart0 = 0;
prevStart1 = tStart;
prevStop = 0;
isStarted = 1;
for t = tStart+1:Nsec 
  if possStart(t) && isStarted
  %     [prevStart0, prevStart1, t]
    possStart(prevStart0) = 0;
    prevStart0 = prevStart1;
    prevStart1 = t;
    isStarted = 1;
  elseif possStart(t)
    prevStart0 = prevStart1;
    prevStart1 = t;
    isStarted = 1;
  end

  if possStop(t)
    if isStarted
      isStarted = 0;
      prevStop = t;
    else
      possStop(t) = 0;
%       error('asdf')
      xlim(t+[-100,100]); pause;
    end
  end
end
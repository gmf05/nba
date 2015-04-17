% parsePossession.m
% Grant Fiddyment, Boston University, 2015/03/06
%
% matlab script to parse ball possession based on NBA play-by-play data
% Note: assumes play-by-play is already encoded as point process data 
%

% load event data
team = 'ATL';
load(['stats2_201415_' team '.mat']); % encoded via nbastats.py

% initialize arrays
Ngames = length(games);
games = reshape(games,[],Ngames)'; % fix game list
sumSec  = [0 cumsum(secPerGame)'];
Nsec = sumSec(end);
rebs0 = zeros(2,Nsec); % split offensive & defensive
orebs0 = zeros(2,Nsec); % split opponent's rebounds into offensive & defensive
possStart = zeros(1,Nsec); % start-possession times for team of interest
possStop = zeros(1,Nsec); % stop-possession times for team of interest
opossStart = zeros(1,Nsec); % start-possession times for opponent
opossStop = zeros(1,Nsec); % stop-possession times for opponent

% get time indices for some relevant events
attempts = shots(1,:) + shots(3,:);
oattempts = oshots(1,:) + oshots(3,:);
misses = shots(1,:) - shots(2,:) + shots(3,:) - shots(4,:);
omisses = oshots(1,:) - oshots(2,:) + oshots(3,:) - oshots(4,:);
missind = find(misses);
omissind = find(omisses);
madeshotind = find(shots(2,:) + shots(4,:));
omadeshotind = find(oshots(2,:) + oshots(4,:));
ftind = find(fts);
oftind = find(ofts);
rebind = find(rebs);
orebind = find(orebs);
toind = find(tos);
otoind = find(otos);

% make list of quarter start/stop times
i = 1;
secPerQtr = zeros(1, 5*Ngames);
for game = 1:Ngames
    secPerQtr(i:i+3) = 720;
    i = i+4;
    if secPerGame(game)>2880 % is there overtime?
        % each overtime is 300 sec
        NOT = (secPerGame(game) - 2880) / 300;
        secPerQtr(i:i+NOT-1) = 300;
        i = i+NOT;
    end
end
secPerQtr(i:end)=[];
sumSecQtr = [0 cumsum(secPerQtr)];
Nqtrs = length(secPerQtr);

% First we must separate rebounds into off & def:

% for each rebound
% find nearest shot
attempts = shots(1,:) + shots(3,:) + fts;
oattempts = oshots(1,:) + oshots(3,:) + ofts;
for i = rebind
    
end
% OR
% for each shot miss, find rebound...?



%% format data types
% saves memory and makes matrix ops easier
% assumes column 1 = date
% columns 2-3 = team & opponent
% columns 4-end = stats listed in variable 'features'
yr = '2008';
fname = ['~/NBASeason' yr '.mat'];
fname2 = ['~/NBASeason' yr '-mod.mat'];

load(fname);
for i = 1:size(games,1)
  i
  for j = 4:size(games,2)
    games{i,j} = str2num(games{i,j});    
  end
end

Ngames = size(games,1);
features = features(4:end,:);
dates = games(:,1);
teams = games(:,2:3);
stats = reshape([games{:,4:end}],Ngames,[]);

% save(fname, 'games', 'features');
save(fname2, 'Ngames', 'features', 'dates', 'teams', 'stats');

%% analysis

% get a team's games
% teamList = cell2str(teams(:,1));
team = 'Heat';
<<<<<<< HEAD
=======
% team = 'Bucks';

>>>>>>> Misc changes
gameind = []; for i = 1:size(teams,1), if isequal(teams{i,1},team), gameind(end+1) = i; end; end

% create a point process of team wins
Ngames = length(gameind); % number of games played (regular season + playoffs)
dn = zeros(1,Ngames);
for n = 1:Ngames
  if stats(gameind(n),2)>0
    dn(n) = 1;
  end
end
d = pp_data(dn);

% does a lead after 3 qtrs improve win probability?
% one example (2012 Heat):
% yes (p=0.017) baseline prob. ~49% -> ~93% with a lead
ftind = [5];
Nfts = length(ftind);
S = stats(gameind,ftind);
Y = d.dn';
X = zeros(Ngames, Nfts+1);
X(:,1) = 1;
i=1;
X(:,i+1) = S(:,i)>0; i=i+1;
% [b,dev,st] = glmfit(X, Y,'poisson','constant','off');
<<<<<<< HEAD
=======
[b,dev,st] = glmfit(X, Y,'binomial','constant','off');
>>>>>>> Misc changes

% more specifically,
% baseline probability of 66% goes up/down 2% per point the team leads/trails
% at end of 3rd quarter


<<<<<<< HEAD
=======

%%

% 
p = pp_params();
p = p.add_covar('rate',0,[0 1],'indicator');
% p = p.add_covar('self-history',1,[1 5 10],'spline');
m = pp_model();
m = m.fit(d,p);
>>>>>>> Misc changes

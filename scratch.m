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
ind = []; for i = 1:size(teams,1), if isequal(teams{i,1},team), ind(end+1) = i; end; end

% create a point process of team wins
Ngames = length(ind); % number of games played (regular season + playoffs)
dn = zeros(1,Ngames);
for n = 1:Ngames
  if stats(ind(n),2)>0
    dn(n) = 1;
  end
end
d = pp_data(dn);

% 
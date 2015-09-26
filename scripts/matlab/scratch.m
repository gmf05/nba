% load NBASeason2013.mat
gameind = find(ismember(teams(:,1), 'Heat'));

teams = {};
Nteams = length(teams);
bs = cell(1, Nteams);
stats = cell(1,Nteams);

% for each team, fit a model
for teamind = 1:Nteams
  y = stats(gameind, 1); % variable of interest: number of points
  statind = 14:19; % covariates: assists, rebounds, steals, blocks
  X = [ones(length(gameind), 1) stats(gameind, statind)];
  % [b, dev, stats] = glmfit(X, y, 'normal', 'constant', 'off');
  [b, st] = glmfit0(X, y, 'identity');
  
  bs{teamind} = b;
  stats{teamind} = st;
end
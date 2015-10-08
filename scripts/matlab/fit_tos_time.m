% teamlist = {'ATL','BOS','CHI','DAL','MIA','OKC','SAS'};
% teamlist = {'ATL','BOS','BKN','CHA','CHI','CLE','DAL','DEN','DET','GSW',...
%   'HOU','IND','LAC','LAL','MEM','MIA','MIL','MIN','NOP','NYK','OKC','ORL',...
%   'PHI','PHX','POR','SAC','SAS','TOR','UTA','WAS'};
teamlist = {'ATL','BOS','BKN','CHA','CHI','DAL','DEN','DET','GSW',...
  'LAC','LAL','MEM','MIA','MIL','MIN','NOP','NYK','OKC','ORL',...
  'PHI','PHX','POR','SAC','SAS','TOR','UTA','WAS'};
% teamlist = {'CHI'};
global DO_CONF_INT PLOT_COLOR
% DO_CONF_INT = false; PLOT_COLOR = 'b';
DO_CONF_INT = true; PLOT_COLOR = 'b';

%%%%%%%%%%%
% load data
team = 'ATL';
load(['stats_201415_' team '.mat']);
Nsec = size(shots,2);
% dn = tos;
% dn = shots(1,:) + shots(3,:); % FGA [all]
dn = shots(2,:) + shots(4,:); % FGM [all]
% dn = shots(1,:); % FGA [2pt]
% dn = shots(2,:); % FGM [2pt]
% dn = shots(3,:); % FGA [3pt]
% dn = shots(4,:); % FGM [3pt]
d = pp_data(dn);
%%%%%%%%%%%

p = pp_params();
response = 1;
% p = p.add_covar('rate',[0],[0 1],'indicator');
p = p.add_covar('rate',[0],[0 0.5 1],'spline');
p = p.add_covar('self-history',response,[1 30 60 90 120],'spline');
% p = p.add_covar('past-success',3,[0],'indicator');
m = pp_model();

% master design matrix X
% initialize arrays
Ngames = length(games);
% games = reshape(games,[],Ngames)'; % fix game list if shaped wrong
sumSec = cumsum(secPerGame);
Nsec = sumSec(end);
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
Ncovar = p.covariate_ind{end}(end);
X = zeros(Nsec, Ncovar);
y = zeros(Nsec, 1);

% for d0 = different subsets over quarters
for n = 1:Nqtrs
  % d0 = this quarter's data
  tn = sumSecQtr(n)+1:sumSecQtr(n+1);
  d0 = d.sub_time_fast(tn).reset_time();
  m0 = m.makeX(d0, p);
  X(tn,:) = m0.X;
  y(tn) = d0.dn(p.response,:);
end
[b, dev, stats] = glmfit(X,y,'poisson','constant','off');
m = pp_model();
m.link = 'log';
m.fit_method = 'glmfit';
m.b = b;
m.W = stats.covb;
m.X = X;
m.y = y;
m.CIF = exp(m.X*m.b);
m = m.calcGOF();

figure, m.plot(d0,p);
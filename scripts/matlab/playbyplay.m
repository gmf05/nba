% team = 'DAL'; col = 'k';
% team = 'MIA'; col = 'r';
% team = 'OKC'; col = 'b';
% team = 'CHI'; col = 'm';
% close all; 
figure

% teams = {'DAL','MIA','OKC','CHI'};
teams = {'SAS','MIA','IND','LAC'};
cols = {'k','r','b','m'};
global PLOT_COLOR
global DO_CONF_INT
DO_CONF_INT = false;

for t = 1:length(teams)
  team = teams{t};
  PLOT_COLOR = cols{t};
%   load([team '2011playoffs.mat']);
  load([team '2014playoffs.mat']);
  Ngames = double(Ngames);

  p = pp_params();
  T_knots = [0:0.25:1]; T_basis = 'spline';
  % T_knots = [0 1]; T_basis = 'indicator';
  Q_knots = [1 20 60 100 150 300];
  % p = p.add_covar('rate',0,T_knots,'spline');
  p = p.add_covar('rate',0,T_knots,T_basis);
  p = p.add_covar('self-history',1,Q_knots,'spline');

  secPerGame = 48*60;
%   ind = 1; modelname = 'two point attempt';
%   ind = 2; modelname = 'two point success';
%   ind = 3; modelname = 'three point attempt';
%   ind = 4; modelname = 'three point success';
  X=[]; y=[];
  for n = 1:Ngames
    dn = shots(ind,(n-1)*secPerGame+(1:secPerGame));
%     dn = fouls((n-1)*secPerGame+(1:secPerGame)); modelname = 'fouls';
    dn = tos((n-1)*secPerGame+(1:secPerGame)); modelname = 'turnovers';
    d = pp_data(dn);
    m = pp_model();
    m = m.makeX(d,p);
    X = [X; m.X];
    y = [y; dn'];
  end

  % dn = shots(ind,:);
  % t = mod(1:48*60*Ngames,48*60);
  % t(t==0)=48*60;
  % d = pp_data(dn,t);

  [b,dev,stats] = glmfit(X,y,'poisson','constant','off');
  W = stats.covb;
  cif = glmval(b,X,'log','constant','off');
  m = pp_model(b,W,X,y,cif,'log');
  m.fit_method = 'glmfit';
  m
  m.plot(d,p)
  subplot(211)
  xlabel('time into game [sec]')
  title([modelname ' rate [per sec]'])
  subplot(212);
  title(['history-dependence in ' modelname])
  xlabel('lag time [sec]')
  update_fig();
end

subplot(211); legend(teams);

% filename = [strrep(modelname, ' ', '_') '.jpg'];
% print(filename,'-djpeg100')

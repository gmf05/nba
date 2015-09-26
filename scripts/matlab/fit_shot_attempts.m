% teamlist = {'ATL','BOS','CHI','DAL','MIA','OKC','SAS'};
% teamlist = {'ATL','BOS','BKN','CHA','CHI','CLE','DAL','DEN','DET','GSW',...
%   'HOU','IND','LAC','LAL','MEM','MIA','MIL','MIN','NOP','NYK','OKC','ORL',...
%   'PHI','PHX','POR','SAC','SAS','TOR','UTA','WAS'};
teamlist = {'ATL','BOS','BKN','CHA','CHI','DAL','DEN','DET','GSW',...
  'LAC','LAL','MEM','MIA','MIL','MIN','NOP','NYK','OKC','ORL',...
  'PHI','PHX','POR','SAC','SAS','TOR','UTA','WAS'};
% teamlist = {'CHI'};
colors = {'k','g','r','m','r','b','k'};
global DO_CONF_INT PLOT_COLOR; 
DO_CONF_INT = false;

for teamInd = 1:length(teamlist)
% for teamInd = 1
%   load(['data/' teamlist{teamInd} '2011playoffs.mat']);
  load(['data/stats_201415_' teamlist{teamInd} '.mat']);

  sh = shots(1:2,:);
  NT = size(sh,2);
  attind = find(sh(1,:));
  attmade = sh(2,attind);
  madeind = find(sh(2,:));
  dn = [sh; zeros(1,NT)];
  for i = 2:length(attind)
    j = find(madeind<attind(i),1,'last');
    if ~isempty(j) && (madeind(j) == attind(i-1))
      dn(3,attind(i)) = 1;
    end
  end
  d = pp_data(dn);
  response = 1;

  p = pp_params();
  p = p.add_covar('rate',[0],[0 1],'indicator');
  p = p.add_covar('self-history',response,[1 30 60 90 120],'spline');
%   p = p.add_covar('past-success',3,[0],'indicator');
  m = pp_model();
  % m = m.makeX(d,p);
  m = m.fit(d,p);
%   m
  [m.b(end) m.stats.p(end)]
  PLOT_COLOR = 'r';
%   PLOT_COLOR = colors{teamInd};
  try, m.plot(d,p); end
end
%% spatial histogram
% d = csvread('shots_00213b.csv');
%d = csvread('shots_0414.csv');
% pts, dist, x, y, made
dx = 3;
dy = 3;
xbins = -250:dx:250;
%ybins = -55:dy:900;
ybins = [-55:dy:300 400:100:900];

[xrect,yrect] = meshgrid(xbins, ybins);
fga = 0*yrect;
fgm = 0*yrect;
for n = 1:size(d,1)
  i = find(ybins>=d(n,4),1,'first');
  j = find(xbins>=d(n,3),1,'first');
  fga(i,j) = fga(i,j) + 1;
  if d(n,5)
    fgm(i,j) = fgm(i,j) + 1;
  end
end

imagesc(xrect(:),yrect(:),fgm./fga)
set(gca,'XTick',[])
set(gca,'YTick',[])
% caxis([0,0.5])

%%

% spatial binning parameters
dx = 50; dy = 50;
xbins = -250:dx:250;
ybins = -55:dy:900;
%ybins = [-55:dy:300 400:100:900];

% load data
% load ATLshots2014.mat
% load BOSshots2014.mat
load shots_BKN.mat

% count fgm, fga by location
fgaind = sum(pp([1 3],:));
xs = pp(5,find(fgaind));
ys = pp(6,find(fgaind));
dist = pp(7,find(fgaind));
fga = hist2d(xs,ys,xbins,ybins);
%caxis([0,20])

fgmind = sum(pp([2 4],:));
xs = pp(5,find(fgmind));
ys = pp(6,find(fgmind));
dist = pp(7,find(fgmind));
[fgm,xrect,yrect] = hist2d(xs,ys,xbins,ybins);
%caxis([0,20])

% FG% by location
fgp = fgm./fga;
fgp(fga==0) = 0;
figure
imagesc(xrect(:), yrect(:), fgp);

%% compare two teams' FG% by location
team1 = 'ATL';
team2 = 'BKN';

team1 = 'GSW';
team2 = 'NOP';

% spatial binning parameters
dx = 15; dy = 15;
dx = 50; dy = 50;
xbins = -250:dx:250;
ybins = -55:dy:900;

% count fgm, fga, FG% by location (team 1)
load([team1 'shots2014.mat']);
fgaind = find(sum(pp([1 3],:)));
xs = pp(5,fgaind);
ys = pp(6,fgaind);
fga1 = hist2d(xs,ys,xbins,ybins);
fgmind = find(sum(pp([2 4],:)))
xs = pp(5,fgmind);
ys = pp(6,fgmind);
[fgm1,xrect,yrect] = hist2d(xs,ys,xbins,ybins);
fgp1 = fgm1./fga1;
fgp1(fga1==0) = 0;

load([team2 'shots2014.mat']);
fgaind = find(sum(pp([1 3],:)));
xs = pp(5,fgaind);
ys = pp(6,fgaind);
fga2 = hist2d(xs,ys,xbins,ybins);
fgmind = find(sum(pp([2 4],:)))
xs = pp(5,fgmind);
ys = pp(6,fgmind);
[fgm2,xrect,yrect] = hist2d(xs,ys,xbins,ybins);
fgp2 = fgm2./fga2;
fgp2(fga2==0) = 0;

fganorm1 = fga1./sum(sum(fga1));
fganorm2 = fga2./sum(sum(fga2));

% figure, imagesc(xrect(:), yrect(:), fganorm1); ylim([-55,400]); caxis([0,0.01])
% figure, imagesc(xrect(:), yrect(:), fganorm2); ylim([-55,400]); caxis([0,0.01])
% figure, imagesc(xrect(:), yrect(:), fganorm1-fganorm2); ylim([-55,400]);

%%%
fgdiff = fgp1-fgp2;
for i = 1:size(xrect,1)
  for j = 1:size(xrect,2)
    if abs(fgdiff(i,j))>0.05
      fgdiff(i,j) = sign(fgdiff(i,j));
    else
      fgdiff(i,j) = 0;
    end
  end
end

% visualize difference
figure, imagesc(xrect(:), yrect(:), fgdiff);
ylim([-55,400]);
% caxis([-0.4,0.4]);

%% point distribution

% team1 = 'ATL';
% team2 = 'BKN';

team1 = 'GSW';
team2 = 'NOP';

% spatial binning parameters
dx = 15; dy = 15;
dx = 50; dy = 50;
xbins = -250:dx:250;
ybins = -55:dy:900;

% compute point distribution by location (team 1)
load([team1 'oshots2014.mat']);
npts = sum(2*pp(2,:) + 3*pp(4,:));
pt2ind = find(pp(2,:));
pt3ind = find(pp(4,:));
xs = pp(5,pt2ind);
ys = pp(6,pt2ind);
[fg2pt,xrect,yrect] = hist2d(xs,ys,xbins,ybins);
xs = pp(5,pt3ind);
ys = pp(6,pt3ind);
[fg3pt,xrect,yrect] = hist2d(xs,ys,xbins,ybins);
ptdist1 = (2*fg2pt + 3*fg3pt) ./ npts;
figure, imagesc(xrect(:), yrect(:), ptdist1);
ylim([-55,400])
caxis([0,0.05])

% compute point distribution by location (team 2)
load([team2 'oshots2014.mat']);
npts = sum(2*pp(2,:) + 3*pp(4,:));
pt2ind = find(pp(2,:));
pt3ind = find(pp(4,:));
xs = pp(5,pt2ind);
ys = pp(6,pt2ind);
[fg2pt,xrect,yrect] = hist2d(xs,ys,xbins,ybins);
xs = pp(5,pt3ind);
ys = pp(6,pt3ind);
[fg3pt,xrect,yrect] = hist2d(xs,ys,xbins,ybins);
ptdist2 = (2*fg2pt + 3*fg3pt) ./ npts;
figure, imagesc(xrect(:), yrect(:), ptdist2);
ylim([-55,400])
caxis([0,0.05])

%% point distribution (comparing offenses and defenses) (2)

% team1 = 'ATL';
% team2 = 'BKN';

% team2 = 'ATL';
% team1 = 'BKN';

% team1 = 'GSW';
% team2 = 'NOP';

% team2 = 'GSW';
% team1 = 'NOP';

% spatial binning parameters
dx = 15; dy = 15;
dx = 50; dy = 50;
xbins = -250:dx:250;
ybins = -55:dy:900;

% compute point distribution by location (team 1)
load([team1 'oshots2014.mat']);
npts = sum(2*pp(2,:) + 3*pp(4,:));
pt2ind = find(pp(2,:));
pt3ind = find(pp(4,:));
xs = pp(5,pt2ind);
ys = pp(6,pt2ind);
[fg2pt,xrect,yrect] = hist2d(xs,ys,xbins,ybins);
xs = pp(5,pt3ind);
ys = pp(6,pt3ind);
% [fg3pt,xrect,yrect] = hist2d(xs,ys,xbins,ybins);
% ptdist1 = (2*fg2pt + 3*fg3pt) ./ npts;
% figure, imagesc(xrect(:), yrect(:), ptdist1);
ylim([-55,400])
caxis([0,0.05])

% compute point distribution by location (team 2)
load([team2 'shots2014.mat']);
npts = sum(2*pp(2,:) + 3*pp(4,:));
pt2ind = find(pp(2,:));
pt3ind = find(pp(4,:));
xs = pp(5,pt2ind);
ys = pp(6,pt2ind);
[fg2pt,xrect,yrect] = hist2d(xs,ys,xbins,ybins);
xs = pp(5,pt3ind);
ys = pp(6,pt3ind);
[fg3pt,xrect,yrect] = hist2d(xs,ys,xbins,ybins);
ptdist2 = (2*fg2pt + 3*fg3pt) ./ npts;
% figure, imagesc(xrect(:), yrect(:), ptdist2);
% ylim([-55,400])
% caxis([0,0.05])

p0 = ptdist1.*ptdist2;
p0 = p0./sum(sum(p0));
figure, imagesc(xrect(:), yrect(:), p0);
ylim([-55,400])
caxis([0,0.01])
title([team2 ' off / ' team1 ' def'])

%% 

response = 1;
load ATLshots2014.mat
run('~/Code/repos/pp_tools/pp_tools.m')

% make times = n secs into game for each game
times = zeros(1,nsecs(end));
for n = 1:82
  times(nsecs(n)+1:nsecs(n+1)) = 1:(nsecs(n+1)-nsecs(n));
end
d = pp_data(pp, times);
d.dn(1,:) = d.dn(1,:) + d.dn(3,:); % fga: 2pt and 3pt

p = pp_params();
p.response = response;
%p = p.add_covar('time',0,[0 1],'indicator');
p = p.add_covar('time',0,[0:0.25:1],'spline');
p = p.add_covar('self-history',response,[1 30 60 90], 'spline');


m = pp_model();
m = m.fit(d0,p);

figure, m.plot(d0,p);

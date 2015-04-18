%% spatial histogram
d = csvread('shots_00213b.csv');
% pts, dist, x, y, made
dx = 10;
dy = 10;
xs = -250:dx:250;
ys = -55:dy:900;
[x,y] = meshgrid(xs, ys);
fga = 0*y;
fgm = 0*y;
for n = 1:size(d,1)
  i = find(ys>=d(n,4),1,'first');
  j = find(xs>=d(n,3),1,'first');
  fga(i,j) = fga(i,j) + 1;
  if d(n,5)
    fgm(i,j) = fgm(i,j) + 1;
  end
end

imagesc(xs(:),ys(:),fgm./fga)
caxis([0,0.5])
set(gca,'XTick',[])
set(gca,'YTick',[])

%%

% spatial binning parameters
dx = 12; dy = 25;
xbins = -250:dx:250;
ybins = -55:dy:900;
ybins = [-55:dy:300 400:100:900];

% load data
load BOSshots2014.mat
load ATLshots2014.mat

% count fgm, fga by location
fgaind = sum(pp([1 3],:));
xs = pp(5,find(fgaind));
ys = pp(6,find(fgaind));
dist = pp(7,find(fgaind));
fga = hist2d(xs,ys,xbins,ybins);
caxis([0,20])

fgmind = sum(pp([2 4],:));
xs = pp(5,find(fgmind));
ys = pp(6,find(fgmind));
dist = pp(7,find(fgmind));
[fgm,xrect,yrect] = hist2d(xs,ys,xbins,ybins);
caxis([0,20])

% FG% by location
fgp = fgm./fga;
fgp(fga==0) = 0;
figure
imagesc(xrect(:), yrect(:), fgp);

%% 

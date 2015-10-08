function [count,xrect,yrect] = hist2d(xs, ys, xbins, ybins)
if nargin==3
  ybins = xbins;
  xbins = ys;
  ys = xs(:,2);
  xs = xs(:,1);
end

[xrect,yrect] = meshgrid(xbins, ybins);
count = 0*xrect;
for n = 1:length(xs)
  i = find(ybins>=ys(n),1,'first');
  j = find(xbins>=xs(n),1,'first');
  count(i,j) = count(i,j) + 1;
end

figure
imagesc(xrect(:),yrect(:),count)

end
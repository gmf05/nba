function [game, qtr, min, sec] = gamesElapsed(nSec, secPerGame)
    sumSec = [0 cumsum(secPerGame)];
    game = find(sumSec>=nSec,1,'first')-1;
    t0 = nSec - sumSec(game);
    qtr = ceil(t0 / 720);
    min = floor((t0 - (qtr-1)*720)/60);
    sec = t0 - (qtr-1)*720 - min*60;
    
    % debug
%     [game, qtr, min, sec]
%     fprintf(['Q' num2str(qtr) ' ' num2str(12-min) ':' num2str(60-sec) '\n']);

end
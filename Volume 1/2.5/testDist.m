function testDist(x)
    clc
    clear
    close all
    lambda = 0.5;
    t=0:0.01:1;
    y=-log(1-t)/lambda+1;
    ceil(y)
    plot(t,y);
    %plot(t,log(1-t));
    grid on
    %y=arrayfun(@(x) mylog(x),t);
    %plot(t, y)
    hold on
    %plot(t,log(1-t))
end

function [y] = mylog(x)
    ord=1:8;
    y=-x.^ord./ord;
    y=sum(y);
    %y=-ord*x.^ord./ord
    %y=x;
%    y = -x - x.^2/2  - x.^3/3 - x.^4/4;
end
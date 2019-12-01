clear;

% resetdir('rawmask');

throbbers = dir;
n = 1;
for i = 1:length(throbbers)
    isThrobber = contains(throbbers(i).name, 'chips');
    if isThrobber
        raw = imread(throbbers(i).name);
        [im, map] = rgb2ind(raw, 256);
        
        if n == 1
            imwrite(im, map, 'throbbers/hi.gif', 'Transparent', 1, 'DisposalMethod', 'restoreBG', 'DelayTime', 0.2, 'LoopCount', inf);
            n = 0;
        else
            imwrite(im, map, 'throbbers/hi.gif', 'Transparent', 1, 'DisposalMethod', 'restoreBG', 'DelayTime', 0.2, 'WriteMode', 'append');
        end
    end
end

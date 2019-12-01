clear;

% resetdir('rawmask');

moves = dir;
for i = 1:length(moves)
    isSM = contains(moves(i).name, '_SM');
    isBB = contains(moves(i).name, '_BB');
    if isSM || isBB
%     if contains(moves(i).name, 'Portrait')
        im = imread(moves(i).name);
        r = im(:, :, 1); % color
        g = im(:, :, 2); % outline
        b = im(:, :, 3); % shading
        
        rbin = uint8(r > 0);
        rmask = 256 * rbin;
        ginv = 256 - g;
        binv = 256 - b;
        
%         imshow([r, rmask; g, ginv; b, binv]);

        imwrite(rbin .* b - ginv, ['moves/', moves(i).name], 'Alpha', rmask + ginv);
    end
end

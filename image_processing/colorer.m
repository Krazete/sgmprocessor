clear;

moves = dir;
for i = 1:length(moves)
    if contains(moves(i).name, 'VariableCutter')
        im = imread(moves(i).name);
        r = im(:, :, 1); % light
        g = im(:, :, 2); % outline
        b = im(:, :, 3); % shadow
        
        rbin = uint8(r > 0);
        rmask = 256 * rbin;
        ginv = 256 - g;
        binv = 256 - b;
        
        R = r;
        G = r;
        B = r;
        
%         unique(r);
%         R(R == 0) = 0x00; G(G == 0) = 0x00; B(B == 0) = 0x00;
        R(r == 4) = 0xf7; G(r == 4) = 0x72; B(r == 4) = 0x95; % outer ear
        R(r == 8) = 0xba; G(r == 8) = 0x4a; B(r == 8) = 0x6c; % inner ear
        R(r == 12) = 0x83; G(r == 12) = 0x5a; B(r == 12) = 0x4f; % bangs
        R(r == 17) = 0xf7; G(r == 17) = 0x72; B(r == 17) = 0x95; % exclamation points
        R(r == 22) = 0x83; G(r == 22) = 0x5a; B(r == 22) = 0x4f; % side hair
        R(r == 27) = 0x83; G(r == 27) = 0x5a; B(r == 27) = 0x4f; % back hair
        R(r == 36) = 0xfe; G(r == 36) = 0xe8; B(r == 36) = 0xd9; % face
        R(r == 40) = 0xff; G(r == 40) = 0xff; B(r == 40) = 0xff; % eye white
        R(r == 43) = 0x25; G(r == 43) = 0x55; B(r == 43) = 0x6d; % inner pupil
        R(r == 46) = 0x74; G(r == 46) = 0xbb; B(r == 46) = 0xaf; % outer pupil
        R(r == 50) = 0xfe; G(r == 50) = 0xe8; B(r == 50) = 0xd9; % mouth
        R(r == 60) = 0x4d; G(r == 60) = 0x44; B(r == 60) = 0x42; % collar, bangles
        R(r == 64) = 0xe6; G(r == 64) = 0xf0; B(r == 64) = 0xf3; % bell
        R(r == 68) = 0xf7; G(r == 68) = 0x72; B(r == 68) = 0x95; % inner bell, inner shoulders
        R(r == 72) = 0xe6; G(r == 72) = 0xf0; B(r == 72) = 0xf3; % ribcage
        R(r == 77) = 0xe6; G(r == 77) = 0xf0; B(r == 77) = 0xf3; % outer shirt
        R(r == 82) = 0xf7; G(r == 82) = 0x72; B(r == 82) = 0x95; % inner shirt
        R(r == 87) = 0xfe; G(r == 87) = 0xe8; B(r == 87) = 0xd9; % midriff
        R(r == 92) = 0x4d; G(r == 92) = 0x44; B(r == 92) = 0x42; % upper hip
        R(r == 96) = 0xe6; G(r == 96) = 0xf0; B(r == 96) = 0xf3; % utility belt
        R(r == 100) = 0xf7; G(r == 100) = 0x72; B(r == 100) = 0x95; % utility belt buckle
        R(r == 105) = 0xe6; G(r == 105) = 0xf0; B(r == 105) = 0xf3; % panty
        R(r == 110) = 0xfe; G(r == 110) = 0xe8; B(r == 110) = 0xd9; % outer shoulder
        R(r == 115) = 0xe6; G(r == 115) = 0xf0; B(r == 115) = 0xf3; % main arm
        R(r == 120) = 0xe6; G(r == 120) = 0xf0; B(r == 120) = 0xf3; % outer connections
        R(r == 125) = 0xe6; G(r == 125) = 0xf0; B(r == 125) = 0xf3; % inner connections
        R(r == 129) = 0xe6; G(r == 129) = 0xf0; B(r == 129) = 0xf3; % opposite elbow
        R(r == 132) = 0xe6; G(r == 132) = 0xf0; B(r == 132) = 0xf3; % elbow
        R(r == 137) = 0xfe; G(r == 137) = 0xe8; B(r == 137) = 0xd9; % palm
        R(r == 142) = 0xfe; G(r == 142) = 0xe8; B(r == 142) = 0xd9; % fingers
        R(r == 146) = 0xf7; G(r == 146) = 0x72; B(r == 146) = 0x95; % nails
        R(r == 150) = 0xfe; G(r == 150) = 0xe8; B(r == 150) = 0xd9; % thighs
        R(r == 155) = 0xfe; G(r == 155) = 0xe8; B(r == 155) = 0xd9; % side of thigh
        R(r == 160) = 0xe6; G(r == 160) = 0xf0; B(r == 160) = 0xf3; % main leg
        R(r == 164) = 0xe6; G(r == 164) = 0xf0; B(r == 164) = 0xf3; % knee
        R(r == 169) = 0xe6; G(r == 169) = 0xf0; B(r == 169) = 0xf3; % shin
        R(r == 174) = 0x4d; G(r == 174) = 0x44; B(r == 174) = 0x42; % heel
        R(r == 179) = 0x4d; G(r == 179) = 0x44; B(r == 179) = 0x42; % foot
        R(r == 192) = 0xf7; G(r == 192) = 0x72; B(r == 192) = 0x95; % tail
        R(r == 196) = 0x4d; G(r == 196) = 0x44; B(r == 196) = 0x42; % innards
        R(r == 205) = 0xf0; G(r == 205) = 0x00; B(r == 205) = 0x00; % 
        R(r == 215) = 0xfb; G(r == 215) = 0xa5; B(r == 215) = 0xb5; % outer electricity
        R(r == 223) = 0xfb; G(r == 223) = 0xa5; B(r == 223) = 0xb5; % magnetic
        R(r == 228) = 0xfb; G(r == 228) = 0xa5; B(r == 228) = 0xb5; % beam
        R(r == 255) = 0xf0; G(r == 255) = 0x00; B(r == 255) = 0x00; % 
%         RoboFortune_BB4_MagneticTrap

        shadestrength = 0.5;
        maskalpha = 1.0;
        
        x = cat(3, ...
            linearburn(R, binv, shadestrength, ginv), ...
            linearburn(G, binv, shadestrength, ginv), ...
            linearburn(B, binv, shadestrength, ginv) ...
        );

        imwrite(x, ['burned/', moves(i).name], 'Alpha', maskalpha * rmask + ginv);
%         break;
    end
end

for n = 1:64
    R = uint8(mod(double(r) * rand * 100, 256));
    G = uint8(mod(double(r) * rand * 100, 256));
    B = uint8(mod(double(r) * rand * 100, 256));
    
    rgb = (cat(3, R, G, B) - binv * rand - ginv);
    [im, map] = rgb2ind(rgb, 256);

    if n == 1
        imwrite(im, map, 'hola.gif', 'DelayTime', 0.1, 'LoopCount', inf);
    else
        imwrite(im, map, 'hola.gif', 'DelayTime', 0.1, 'WriteMode', 'append');
    end
end

imwrite(r, 'hi.gif', 'DelayTime', 0.1, 'LoopCount', inf);
imwrite(b, 'hi.gif', 'DelayTime', 0.1, 'WriteMode', 'append');
imwrite(g, 'hi.gif', 'DelayTime', 0.1, 'WriteMode', 'append');

function burned = linearburn(target, blendinv, blendopacity, outline)
    burned = target - blendinv * blendopacity - outline;
end

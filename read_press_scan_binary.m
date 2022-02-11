function [t_frame, t_trig, pres, temp,scan_data] = read_press_scan_binary(filename,N_frame)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script reads the output binary file of the MPS4264 pressure scanner.
%
%
% Inputs:
% filename : the name of the file in string (including folder)
% N_frame  : number of frames, omit or set to [] for automatic detection
%
% Outputs:
% scan_data : the full scanned data, 87 parameters
% t_frame         : time stamp of each frame in seconds
% t_trig         : time stamp of each trig in seconds
% temp      : internal temperatures (8 channels)
% pres      : pressure data (64 channels)
%
% Revision history:
% Date          Author(s)     Vers.      Notes
% 2019-02-08    Leon Li       1.0        Initial release
% 2019-02-08    ØWP           1.1        Changed to work with bridge data
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% number of rows in the binary scan:
%   87 - Normal scan
%   87 - Fast scan
%   471 - Statistical scan
% channel grouping for fast scan


%% Handle inputs

if nargin==1
    N_frame=[];
end

if isempty(N_frame)
    N_frame=5e5; % Set to high number (more than actual frames)
end

if exist(filename)~=2
   error('File appears to not exist. Check file name.') 
end


%% Read data

fileID = fopen(filename);

part_1 = nan(4,N_frame); % packet type, packet size, frame number, scan type
part_2 = nan(1, N_frame); % frame rate
part_3 = nan(2, N_frame); % valve status, units index
part_4 = nan(1, N_frame); % unit conversion factor
part_5 = nan(2, N_frame); % PTP scan start time (sec), PTP scan start time (ns)
part_6 = nan(1, N_frame); % External trigger time
part_7 = nan(72, N_frame); % temperatures (x8), pressures (x64)
part_8 = nan(4, N_frame); % frame time (sec), frame time (ns), external trigger time (sec), external trigger time (ns)

N_frame_stop=[];

for i = 1:N_frame
    
        part_1_temp = fread(fileID,4,'int32');
    
        % Check if this line is empty
        if isempty(part_1_temp)
            N_frame_stop=i-1;
            disp(['***** Stopped reading at ' num2str(N_frame_stop) ' frames']);
            break
        end
        
        part_1(:,i)=part_1_temp;
        part_2(:,i) = fread(fileID,1,'float32');
        part_3(:,i) = fread(fileID,2,'int32');
        part_4(:,i) = fread(fileID,1,'float32');
        part_5(:,i) = fread(fileID,2,'int32');
        part_6(:,i) = fread(fileID,1,'uint32');
        part_7(:,i) = fread(fileID,72,'float32');
        part_8(:,i) = fread(fileID,4,'int32');

end

% Cut to read frames only
if ~isempty(N_frame_stop)
    part_1=part_1(:,1:N_frame_stop);
    part_2=part_2(:,1:N_frame_stop);
    part_3=part_3(:,1:N_frame_stop);
    part_4=part_4(:,1:N_frame_stop);
    part_5=part_5(:,1:N_frame_stop);
    part_6=part_6(:,1:N_frame_stop);
    part_7=part_7(:,1:N_frame_stop);
    part_8=part_8(:,1:N_frame_stop);
end

fclose(fileID);

scan_data = [part_1;part_2;part_3;part_4;part_5;part_6;part_7;part_8].';

t_frame = scan_data(:,84) + scan_data(:,85)/1e9; %Time the frame occurred, Time in s plus time in ns
t_trig = scan_data(:,86) + scan_data(:,87)/1e9; %Time the external trigger occurred , Time in s plus time in ns

temp = scan_data(:,12:19);
pres = scan_data(:,20:83);

return
%% plot
% 
% g1 = [1 5 9 13 17 21 25 29 36 40 44 48 52 56 60 64];
% g2 = [2 6 10 14 18 22 26 30 35 39 43 47 51 55 59 63];
% g3 = [3 7 11 15 19 23 27 31 34 38 42 46 50 54 58 62];
% g4 = [4 8 12 16 20 24 28 32 33 37 41 45 49 53 57 61];
% 
% % figure;
% % plot(t,temp);
% % xlabel('t (s)');
% % ylabel('Temp (C)');
% % box on;
% figure;
% switch gp
%     case 0
%         plot(t,pres);
%     case 1
%         plot(t,pres(:,g1));
%     case 2
%         plot(t,pres(:,g2));
%     case 3
%         plot(t,pres(:,g3));
%     case 4
%         plot(t,pres(:,g4));
% end
% xlabel('t (s)');
% ylabel('Press (Pa)');
% box on;
% end
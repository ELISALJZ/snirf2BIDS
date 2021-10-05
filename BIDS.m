% Example on how to get required information into BIDS format. The variable
% s is a SnirfClass where s = SnirfClass(filename)

%% Channels

% Allocating space for sections of Channel description
name = cell(length(s.data.measurementList),1); % Where s is the SnirfClass('snirffile')
source = zeros(length(s.data.measurementList),1);
detector = zeros(length(s.data.measurementList),1);
wavelength_nominal = zeros(length(s.data.measurementList),1);

% Needs to be included
% - type: dataTypeIndex
% - units


% This for-loop will fill sections with required data
for i = 1:length(s.data.measurementList)
    source(i) = s.data.measurementList(1,i).sourceIndex; % SnirfFile -> Data -> Measurement List -> 
    detector(i)= s.data.measurementList(1,i).detectorIndex;
    wavelength_nominal(i) = s.probe.wavelengths(s.data.measurementList(1,i).wavelengthIndex);
    name(i) = strcat(s.probe.sourceLabels(source(i)),{'_'},s.probe.detectorLabels(detector(i)),{' '},str2cell(num2str(wavelength_nominal(i))));
end

% Creating a table for the data set
T = table(name,source,detector,wavelength_nominal);
writetable(T,'table.txt','Delimiter','\t','WriteRowNames',true);

%% Optode Description

% Get names
nameS = s.probe.sourceLabels;
nameD = s.probe.detectorLabels;
name = [nameS;nameD];

% Get type
type = cell(length(name),1);
for i = 1:length(name)
    if (name{i}(1) == 'S')
        type{i} = 'source';
    else
        type{i} = 'detector';
    end
end

% Get Positions
sourcePosx = s.probe.sourcePos3D(:,1);
detectorPosx = s.probe.detectorPos3D(:,2);
sourcePosy = s.probe.sourcePos3D(:,2);
detectorPosy = s.probe.detectorPos3D(:,2);
sourcePosz = s.probe.sourcePos3D(:,3);
detectorPosz = s.probe.detectorPos3D(:,3);
x = [sourcePosx;detectorPosx];
y = [sourcePosy;detectorPosy];
z = [sourcePosz;detectorPosz];

% Creating a table for the data set
T2 = table(name,type,x,y,z);
writetable(T2,'table2.txt','Delimiter','\t','WriteRowNames',true);
%% Sidecar JSON


% Example of how to easily write a json file in correct format. A struct
% will need to be made to include the necessary information in the sidecar
fid = fopen('this.json','w');
jsonc = jsonencode(s.metaDataTags.tags,'PrettyPrint',true); % PrettyPrint only included in Matlab 2021
fprintf(fid,jsonc);
fclose(fid);
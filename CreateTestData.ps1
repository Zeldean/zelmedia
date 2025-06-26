# Define base directory for movie folder structure
$baseDir = "C:\Users\Zeldean\Desktop\Movie manager Test\IN"
$movieFileExtension = ".mp4"  # Movie file extension
$movieSizeMB = 10  # Size of each dummy movie file in MB

# Movie names based on your example
$movies = @(
    "Birds.Of.Prey.And.The.Fantabulous.Emancipation.Of.One.Harley.Quinn.2020.1080p.BluRay.x264.AAC5.1-[YTS.MX]",
    "Jurassic.World.Dominion.2022.1080p.BluRay.x264.AAC5.1-[YTS.MX]",
    "Lamp.Life.2020.1080p.WEBRip.x264.AAC5.1-[YTS.MX]",
    "Lightyear.2022.1080p.BluRay.x264.AAC5.1-[YTS.MX]",
    "Megamind.2010.1080p.BluRay.x264.AAC5.1-[YTS.MX]",
    "Ready.Player.One.2018.1080p.BluRay.x264-[YTS.AM]",
    "The.Mitchells.Vs.The.Machines.2021.1080p.BluRay.x264.AAC5.1-[YTS.MX]",
    "The.Sea.Beast.2022.1080p.WEBRip.x264.AAC5.1-[YTS.MX]",
    "Toy.Story.1995.1080p.BRrip.x264.YIFY",
    "Toy.Story.2.1999.1080p.BRrip.x264.YIFY",
    "Toy.Story.That.Time.Forgot.2014.1080p.BluRay.x264.AAC5.1-[YTS.MX]",
    "Toy.Story.Toons.Partysaurus.Rex.2012.1080p.BluRay.x264-[YTS.AM]",
    "Inception.2010.1080p.BluRay.x264.AAC5.1-[YTS.MX]",
    "Spider-Man.No.Way.Home.2021.1080p.BluRay.x264.AAC5.1-[YTS.MX]",
    "The.Matrix.1999.1080p.BluRay.x264.AAC5.1-[YTS.MX]",
    "Finding.Nemo.2003.1080p.BluRay.x264.AAC5.1-[YTS.AM]",
    "The.Lion.King.1994.1080p.BluRay.x264.AAC5.1-[YTS.MX]",
    "Frozen.2013.1080p.BluRay.x264.AAC5.1-[YTS.AM]",
    "The.Social.Network.2010.1080p.BluRay.x264.AAC5.1-[YTS.MX]",
    "Guardians.Of.The.Galaxy.2014.1080p.BluRay.x264.AAC5.1-[YTS.MX]",
    "Avengers.Endgame.2019.1080p.BluRay.x264.AAC5.1-[YTS.MX]",
    "Toy.Story.3.2010.1080p.BluRay.x264.AAC5.1-[YTS.MX]"
)

# Create base directory if it doesn't exist
if (!(Test-Path $baseDir)) {
    New-Item -ItemType Directory -Path $baseDir
}

# Function to create a dummy movie file with a given size (in MB)
function CreateDummyFile($path, $sizeMB) {
    $sizeBytes = $sizeMB * 1MB
    $file = New-Object byte[] $sizeBytes
    [System.IO.File]::WriteAllBytes($path, $file)
}

# Create subfolders and dummy movie files with progress bar
$totalMovies = $movies.Count
for ($i = 0; $i -lt $totalMovies; $i++) {
    # Define folder and movie file name
    $movieName = $movies[$i]
    $folderPath = Join-Path $baseDir $movieName
    $movieFilePath = Join-Path $folderPath "$movieName$movieFileExtension"

    # Create subfolder if it doesn't exist
    if (!(Test-Path $folderPath)) {
        New-Item -ItemType Directory -Path $folderPath
    }

    # Create dummy movie file
    CreateDummyFile -path $movieFilePath -sizeMB $movieSizeMB

    # Show progress
    $progressPercent = [math]::Round((($i + 1) / $totalMovies) * 100)
    Write-Progress -Activity "Creating Movie Folders and Files" -Status "Progress: $progressPercent%" -PercentComplete $progressPercent
}

Write-Host "All movie folders and files have been created successfully."

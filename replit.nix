{pkgs}: {
  deps = [
    pkgs.ffmpeg-full
    pkgs.libsndfile
    pkgs.postgresql
    pkgs.glibcLocales
  ];
}

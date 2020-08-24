from schemas import MusicData, MusicMetadata


def music_register(imongo, music_data: MusicData) -> None:

    for landmark in music_data.music_landmark:
        imongo.insert_music(music_data.music_id, str(landmark[0]), int(landmark[1]))


def music_metadata_register(imongo, music_metadata: MusicMetadata) -> None:

    imongo.insert_music_metadata(music_metadata.music_id, music_metadata.title, music_metadata.duration)

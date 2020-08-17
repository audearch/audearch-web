from schemas import MusicData, MusicMetadata


def music_register(imongo, music_data: MusicData) -> None:

    for landmark in music_data.music_landmark:
        imongo.insert_music(music_data.music_id, landmark[0], landmark[1])


def music_metadata_register(imongo, music_metadata: MusicMetadata) -> None:

    imongo.insert_music_metadata(music_metadata)

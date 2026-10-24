package io.github.jqssun.airplay.cast

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class CastMediaUrlTest {
    @Test fun acceptsNetworkVideoLocations() {
        listOf(
            "https://example.com/video.mp4",
            "http://192.168.1.3:8080/video.m3u8?token=example",
            "HTTPS://example.com/video",
            "http://[::1]:8080/video.mp4",
        ).forEach { assertTrue(CastMediaUrl.isSupported(it)) }
    }

    @Test fun rejectsInvalidAndLocalLocations() {
        listOf(
            null, "", " ", "/video.mp4", "//example.com/video.mp4",
            "file:///sdcard/video.mp4", "content://media/video/1", "data:video/mp4;base64,AA",
            "ftp://example.com/video.mp4", "https:///video.mp4", "https://:443/video.mp4",
            "https://user:password@example.com/video.mp4", "http://user@example.com/video.mp4",
            "https://example.com:0/video.mp4", "https://example.com:99999/video.mp4",
            "https://example.com/video with spaces.mp4", " https://example.com/video.mp4",
            "https://example.com\\@other.example/video.mp4",
        ).forEach { assertFalse(CastMediaUrl.isSupported(it)) }
    }

    @Test fun acceptsOnlySupportedMediaTypes() {
        listOf(null, "", "video/mp4", "video/webm", "application/x-mpegURL",
            "application/vnd.apple.mpegurl", "video/mp4; codecs=avc1", "application/octet-stream")
            .forEach { assertTrue(CastMediaUrl.isSupportedMimeType(it)) }
        listOf("text/html", "audio/mpeg", "application/dash+xml", "application/json")
            .forEach { assertFalse(CastMediaUrl.isSupportedMimeType(it)) }
    }
}

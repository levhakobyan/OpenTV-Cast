package io.github.jqssun.airplay.cast

import java.net.URI

/** The receiver accepts network media, never local files or embedded credentials. */
internal object CastMediaUrl {
    fun isSupported(value: String?): Boolean {
        if (value.isNullOrBlank() || value != value.trim()) return false
        return try {
            val uri = URI(value)
            (uri.scheme.equals("http", ignoreCase = true) ||
                uri.scheme.equals("https", ignoreCase = true)) &&
                !uri.host.isNullOrBlank() && uri.rawUserInfo == null &&
                (uri.port == -1 || uri.port in 1..65535)
        } catch (_: Exception) {
            false
        }
    }

    fun isSupportedMimeType(value: String?): Boolean {
        val mime = value?.substringBefore(';')?.trim()?.lowercase().orEmpty()
        return mime.isEmpty() || mime.startsWith("video/") ||
            mime == "application/x-mpegurl" || mime == "application/vnd.apple.mpegurl" ||
            mime == "application/octet-stream"
    }
}

package io.github.jqssun.airplay.cast

import android.app.Activity
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Bundle
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.SystemClock
import android.support.v4.media.MediaMetadataCompat
import android.support.v4.media.session.MediaSessionCompat
import android.support.v4.media.session.PlaybackStateCompat
import android.view.Gravity
import android.view.KeyEvent
import android.view.View
import android.view.WindowManager
import android.widget.FrameLayout
import android.widget.TextView
import androidx.media3.common.AudioAttributes
import androidx.media3.common.C
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import com.google.android.gms.cast.MediaError
import com.google.android.gms.cast.MediaLoadRequestData
import com.google.android.gms.cast.MediaMetadata
import com.google.android.gms.cast.tv.CastReceiverContext
import com.google.android.gms.cast.tv.media.MediaException
import com.google.android.gms.cast.tv.media.MediaLoadCommandCallback
import com.google.android.gms.cast.tv.media.MediaManager
import com.google.android.gms.common.ConnectionResult
import com.google.android.gms.common.GoogleApiAvailability
import com.google.android.gms.tasks.Task
import com.google.android.gms.tasks.TaskCompletionSource
import com.google.android.gms.tasks.Tasks
import io.github.jqssun.airplay.service.AirPlayService

/** A bounded Cast Connect video receiver; registration and a compatible sender are required. */
@androidx.annotation.OptIn(androidx.media3.common.util.UnstableApi::class)
class CastPlaybackActivity : Activity() {
    private val handler = Handler(Looper.getMainLooper())
    private val incomingIntents = ArrayDeque<Intent>()
    private var receiverContext: CastReceiverContext? = null
    private var mediaManager: MediaManager? = null
    private var player: ExoPlayer? = null
    private var session: MediaSessionCompat? = null
    private lateinit var playerView: PlayerView
    private lateinit var statusView: TextView
    private var foreground = false
    private var receiverStarted = false
    private var receiverEventsRegistered = false
    private var pendingLoad: PendingLoad? = null
    private var currentTitle = "Cast video"
    private val receiverEvents = object : CastReceiverContext.EventCallback() {
        override fun onStopApplication() {
            runOnUiThread {
                // Ignore events queued before an intentional foreground teardown.
                if (receiverStarted) {
                    foreground = false
                    failPendingLoad()
                    player?.stop()
                    updateMediaSession()
                    finish()
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        playerView = PlayerView(this).apply { visibility = View.GONE }
        statusView = TextView(this).apply {
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.BLACK)
            textSize = 22f
            gravity = Gravity.CENTER
            val padding = (32 * resources.displayMetrics.density).toInt()
            setPadding(padding, padding, padding, padding)
        }
        setContentView(FrameLayout(this).apply {
            setBackgroundColor(Color.BLACK)
            addView(playerView, FrameLayout.LayoutParams(-1, -1))
            addView(statusView, FrameLayout.LayoutParams(-1, -1))
        })
        showStatus(SETUP_TEXT)
        // Do not replay a completed load when Android recreates the activity.
        if (savedInstanceState == null) incomingIntents.addLast(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        incomingIntents.addLast(intent)
        if (foreground && receiverStarted) processIntents()
    }

    override fun onStart() {
        super.onStart()
        foreground = true
        if (!initializeReceiver()) {
            incomingIntents.clear()
            return
        }
        try {
            // Register callbacks and the token before the SDK can deliver any intent loads.
            initializePlayer()
            mediaManager!!.setMediaLoadCommandCallback(loadCallback)
            mediaManager!!.setSessionCompatToken(session!!.sessionToken)
            session!!.isActive = true
            receiverContext!!.registerEventCallback(receiverEvents)
            receiverEventsRegistered = true
            receiverStarted = true
            receiverContext!!.start()
            if (foreground && !isFinishing) processIntents()
        } catch (_: RuntimeException) {
            showStatus("Cast Connect could not start on this device.\n\n$SETUP_TEXT")
            stopReceiver()
        } catch (_: LinkageError) {
            showStatus("Cast Connect is unavailable on this device.\n\n$SETUP_TEXT")
            stopReceiver()
        }
    }

    override fun onStop() {
        foreground = false
        failPendingLoad()
        // Video has no background playback: publish stopped state before stopping Cast.
        player?.stop()
        updateMediaSession()
        stopReceiver()
        releasePlayer()
        showStatus(SETUP_TEXT)
        super.onStop()
    }

    override fun onDestroy() {
        foreground = false
        failPendingLoad()
        // Leave any already posted SDK callback runnable in the queue: it will see
        // foreground=false and complete its Task with failure instead of hanging.
        releasePlayer()
        super.onDestroy()
    }

    override fun dispatchKeyEvent(event: KeyEvent): Boolean =
        if (playerView.visibility == View.VISIBLE && playerView.dispatchKeyEvent(event)) true
        else super.dispatchKeyEvent(event)

    private fun initializeReceiver(): Boolean {
        if (!packageManager.hasSystemFeature(PackageManager.FEATURE_LEANBACK)) {
            showStatus("Cast Connect requires a supported Android TV device.\n\n$SETUP_TEXT")
            return false
        }
        return try {
            if (GoogleApiAvailability.getInstance().isGooglePlayServicesAvailable(this) !=
                ConnectionResult.SUCCESS
            ) {
                showStatus("Google Play services must be available and up to date.\n\n$SETUP_TEXT")
                false
            } else {
                // initInstance is idempotent. The SDK's getInstance nullability
                // annotation disagrees with its uninitialized runtime value.
                CastReceiverContext.initInstance(applicationContext)
                receiverContext = CastReceiverContext.getInstance()
                mediaManager = receiverContext!!.mediaManager
                true
            }
        } catch (_: RuntimeException) {
            showStatus("Cast Connect is unavailable on this device.\n\n$SETUP_TEXT")
            false
        } catch (_: LinkageError) {
            showStatus("Cast Connect is unavailable on this device.\n\n$SETUP_TEXT")
            false
        }
    }

    private fun initializePlayer() {
        if (player != null) return
        val newPlayer = ExoPlayer.Builder(this).build().apply {
            setAudioAttributes(AudioAttributes.Builder().setUsage(C.USAGE_MEDIA)
                .setContentType(C.AUDIO_CONTENT_TYPE_MOVIE).build(), true)
            setHandleAudioBecomingNoisy(true)
            addListener(object : Player.Listener {
                override fun onEvents(player: Player, events: Player.Events) {
                    updateMediaSession()
                    if (player.playerError != null) {
                        showStatus("This video could not be played. Send a supported direct video URL.\n\n$SETUP_TEXT")
                    }
                }
            })
        }
        player = newPlayer
        playerView.player = newPlayer
        session = MediaSessionCompat(this, "CastPlayback").apply {
            setCallback(object : MediaSessionCompat.Callback() {
                override fun onPlay() { player?.play() }
                override fun onPause() { player?.pause() }
                override fun onSeekTo(pos: Long) { player?.seekTo(pos.coerceAtLeast(0)) }
                override fun onStop() {
                    failPendingLoad()
                    player?.stop()
                    updateMediaSession()
                    showStatus(SETUP_TEXT)
                }
            }, handler)
        }
        updateMediaSession()
    }

    private fun processIntents() {
        val manager = mediaManager ?: return
        while (incomingIntents.isNotEmpty()) {
            val next = incomingIntents.removeFirst()
            try {
                manager.onNewIntent(next)
            } catch (_: RuntimeException) {
                showStatus("The Cast request could not be read.\n\n$SETUP_TEXT")
            }
        }
    }

    private val loadCallback = object : MediaLoadCommandCallback() {
        override fun onLoad(senderId: String?, requestData: MediaLoadRequestData): Task<MediaLoadRequestData> {
            // SDK callbacks normally use the main thread. Marshal defensively before any state change.
            if (Looper.myLooper() != Looper.getMainLooper()) {
                val result = TaskCompletionSource<MediaLoadRequestData>()
                handler.post {
                    acceptLoad(requestData).addOnCompleteListener { completed ->
                        if (completed.isSuccessful) result.trySetResult(completed.result)
                        else result.trySetException(completed.exception ?: loadFailure())
                    }
                }
                return result.task
            }
            return acceptLoad(requestData)
        }
    }

    private fun acceptLoad(request: MediaLoadRequestData): Task<MediaLoadRequestData> {
        val info = request.mediaInfo
        val url = info?.contentUrl?.takeIf { it.isNotBlank() } ?: info?.contentId
        if (!foreground || !receiverStarted || info == null ||
            request.queueData != null || !request.credentials.isNullOrEmpty() ||
            !CastMediaUrl.isSupported(url) || !CastMediaUrl.isSupportedMimeType(info.contentType) ||
            !request.playbackRate.isFinite() || request.playbackRate <= 0 ||
            request.currentTime < MediaLoadRequestData.PLAY_POSITION_UNASSIGNED
        ) {
            return Tasks.forException(loadFailure())
        }
        failPendingLoad()
        // This binding is intentionally delayed until validation succeeds. Merely opening
        // the setup screen must not interrupt an AirPlay connection.
        val pending = PendingLoad(request, url!!)
        pendingLoad = pending
        pending.bind()
        return pending.result.task
    }

    private inner class PendingLoad(val request: MediaLoadRequestData, val url: String) : ServiceConnection {
        val result = TaskCompletionSource<MediaLoadRequestData>()
        private var bound = false
        private val timeout = Runnable { if (pendingLoad === this) failPendingLoad() }

        fun bind() {
            try {
                bound = bindService(Intent(this@CastPlaybackActivity, AirPlayService::class.java),
                    this, Context.BIND_AUTO_CREATE)
                if (bound) handler.postDelayed(timeout, 5_000)
                else failPendingLoad()
            } catch (_: RuntimeException) {
                failPendingLoad()
            }
        }

        override fun onServiceConnected(name: ComponentName, binder: IBinder) {
            if (pendingLoad !== this || !foreground) return
            try {
                val service = (binder as? AirPlayService.LocalBinder)?.service
                    ?: throw IllegalStateException("Receiver service unavailable")
                if (service.serverState.value == AirPlayService.ServerState.RUNNING) {
                    airPlayResumeRequested = true
                }
                service.stopServer()
                detach()
                val currentPlayer = player ?: throw IllegalStateException("Player unavailable")
                currentTitle = request.mediaInfo?.metadata?.getString(MediaMetadata.KEY_TITLE)
                    ?.takeIf { it.isNotBlank() } ?: "Cast video"
                val item = MediaItem.Builder().setUri(url).apply {
                    request.mediaInfo?.contentType?.substringBefore(';')?.trim()
                        ?.takeIf { it.isNotBlank() }?.let(::setMimeType)
                }.build()
                currentPlayer.setMediaItem(item,
                    if (request.currentTime == MediaLoadRequestData.PLAY_POSITION_UNASSIGNED)
                        C.TIME_UNSET else request.currentTime)
                currentPlayer.setPlaybackSpeed(request.playbackRate.toFloat())
                currentPlayer.playWhenReady = request.autoplay != false
                mediaManager!!.setDataFromLoad(request)
                currentPlayer.prepare()
                statusView.visibility = View.GONE
                playerView.visibility = View.VISIBLE
                playerView.requestFocus()
                updateMediaSession()
                pendingLoad = null
                result.trySetResult(request)
            } catch (_: RuntimeException) {
                failPendingLoad()
                showStatus("The Cast video could not be loaded.\n\n$SETUP_TEXT")
            }
        }

        override fun onServiceDisconnected(name: ComponentName) { if (pendingLoad === this) failPendingLoad() }
        override fun onNullBinding(name: ComponentName) { if (pendingLoad === this) failPendingLoad() }
        override fun onBindingDied(name: ComponentName) { if (pendingLoad === this) failPendingLoad() }

        fun detach() {
            handler.removeCallbacks(timeout)
            if (bound) {
                bound = false
                unbindService(this)
            }
        }
    }

    private fun failPendingLoad() {
        val pending = pendingLoad ?: return
        pendingLoad = null
        pending.detach()
        pending.result.trySetException(loadFailure())
    }

    private fun updateMediaSession() {
        val currentPlayer = player ?: return
        val currentSession = session ?: return
        val state = when {
            currentPlayer.playerError != null -> PlaybackStateCompat.STATE_ERROR
            currentPlayer.playbackState == Player.STATE_IDLE -> PlaybackStateCompat.STATE_STOPPED
            currentPlayer.playbackState == Player.STATE_ENDED -> PlaybackStateCompat.STATE_STOPPED
            currentPlayer.playbackState == Player.STATE_BUFFERING -> PlaybackStateCompat.STATE_BUFFERING
            currentPlayer.isPlaying -> PlaybackStateCompat.STATE_PLAYING
            else -> PlaybackStateCompat.STATE_PAUSED
        }
        val actions = PlaybackStateCompat.ACTION_PLAY or PlaybackStateCompat.ACTION_PAUSE or
            PlaybackStateCompat.ACTION_PLAY_PAUSE or PlaybackStateCompat.ACTION_STOP or
            (if (currentPlayer.isCurrentMediaItemSeekable) PlaybackStateCompat.ACTION_SEEK_TO else 0L)
        currentSession.setMetadata(MediaMetadataCompat.Builder()
            .putString(MediaMetadataCompat.METADATA_KEY_TITLE, currentTitle)
            .putLong(MediaMetadataCompat.METADATA_KEY_DURATION,
                currentPlayer.duration.takeIf { it != C.TIME_UNSET }?.coerceAtLeast(0) ?: 0)
            .build())
        currentSession.setPlaybackState(PlaybackStateCompat.Builder().setActions(actions)
            .setState(state, currentPlayer.currentPosition.coerceAtLeast(0),
                if (currentPlayer.isPlaying) currentPlayer.playbackParameters.speed else 0f,
                SystemClock.elapsedRealtime())
            .setBufferedPosition(currentPlayer.bufferedPosition.coerceAtLeast(0))
            .apply {
                if (state == PlaybackStateCompat.STATE_ERROR) {
                    setErrorMessage(PlaybackStateCompat.ERROR_CODE_APP_ERROR, "Video playback failed")
                }
            }
            .build())
        if (receiverStarted) {
            try {
                mediaManager?.broadcastMediaStatus()
            } catch (_: RuntimeException) {
                // Google Play services may disappear while playback is running.
            }
        }
    }

    private fun stopReceiver() {
        val wasStarted = receiverStarted
        receiverStarted = false
        try {
            if (receiverEventsRegistered) {
                receiverContext?.unregisterEventCallback(receiverEvents)
                receiverEventsRegistered = false
            }
            // Default SDK callback rejects loads and does not retain this activity.
            mediaManager?.setMediaLoadCommandCallback(MediaLoadCommandCallback())
            mediaManager?.setSessionCompatToken(null)
            if (wasStarted) receiverContext?.stop()
        } catch (_: RuntimeException) {
            // Unsupported or removed Google Play services must not crash normal app use.
        }
    }

    private fun releasePlayer() {
        playerView.player = null
        player?.release()
        player = null
        session?.release()
        session = null
    }

    private fun showStatus(message: String) {
        playerView.visibility = View.GONE
        statusView.text = message
        statusView.visibility = View.VISIBLE
    }

    companion object {
        private var airPlayResumeRequested = false
        private const val SETUP_TEXT = "Cast Connect receiver\n\nRequires receiver registration and a compatible sender. " +
            "Use built-in Google Cast for Android screen mirroring and apps such as YouTube."

        /** Consumed by the home activity after returning from an actual AirPlay takeover. */
        @JvmStatic fun consumeAirPlayResumeRequest(): Boolean = airPlayResumeRequested.also {
            airPlayResumeRequested = false
        }

        private fun loadFailure(): MediaException = MediaException(MediaError.Builder()
            .setDetailedErrorCode(MediaError.DetailedErrorCode.LOAD_FAILED)
            .setReason(MediaError.ERROR_REASON_INVALID_REQUEST).build())
    }
}

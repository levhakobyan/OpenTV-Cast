#!/usr/bin/env python3
"""Run real renderer Kotlin against deterministic JVM platform fakes.

Requires JDK 21 and the Kotlin compiler jars already downloaded by Gradle.
This checks threading/lifecycle contracts, not Android decoding or TV smoothness.
Usage: JAVA_HOME=... GRADLE_USER_HOME=... python3 tools/tests/video_renderer_regression.py
"""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
CACHE = Path(os.environ.get("GRADLE_USER_HOME", Path.home() / ".gradle")) / "caches/modules-2/files-2.1"
JAVA = Path(os.environ["JAVA_HOME"]) / "bin/java"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--renderer-dir", type=Path,
                    default=ROOT / "app/src/main/kotlin/io/github/jqssun/airplay/renderer")
arguments = parser.parse_args()

def jar(group, artifact, version="*"):
    candidates = sorted((CACHE / group / artifact).glob(f"{version}/*/{artifact}-*.jar"))
    if not candidates:
        raise SystemExit(f"Missing cached {artifact}; run the project's Gradle build first")
    return candidates[-1]

compiler = jar("org.jetbrains.kotlin", "kotlin-compiler-embeddable")
version = compiler.parent.parent.name
stdlib = jar("org.jetbrains.kotlin", "kotlin-stdlib", version)
pom = next(compiler.parent.parent.glob("*/*.pom"))
namespace = {"m": "http://maven.apache.org/POM/4.0.0"}
compiler_dependencies = [jar(dependency.findtext("m:groupId", namespaces=namespace),
                             dependency.findtext("m:artifactId", namespaces=namespace),
                             dependency.findtext("m:version", namespaces=namespace))
                         for dependency in ET.parse(pom).findall("m:dependencies/m:dependency", namespace)]
compiler_cp = os.pathsep.join(map(str, [compiler, *compiler_dependencies,
                                      jar("org.jetbrains", "annotations")]))

SOURCES = {
    "Context.kt": "package android.content\nclass Context",
    "Log.kt": """package android.util
object Log {
    fun i(tag: String, message: String) = 0
    fun w(tag: String, message: String, error: Throwable? = null) = 0
    fun e(tag: String, message: String, error: Throwable? = null) = 0
}
""",
    "Os.kt": """package android.os
import java.util.concurrent.LinkedBlockingQueue
object Build { object VERSION { const val SDK_INT = 30 } }
class Looper {
    val queue = LinkedBlockingQueue<Runnable>()
    companion object { val main = Looper() }
}
class Handler(val looper: Looper) {
    fun post(task: Runnable) { looper.queue.add(task) }
}
class HandlerThread(name: String) : Thread(name) {
    val looper = Looper()
    @Volatile private var accepting = true
    override fun run() {
        while (accepting || looper.queue.isNotEmpty()) looper.queue.take().run()
    }
    fun quitSafely(): Boolean { accepting = false; looper.queue.add(Runnable {}); return true }
}
""",
    "Surface.kt": """package android.view
import android.graphics.SurfaceTexture
class Surface(val texture: SurfaceTexture? = null) {
    var isValid = true
    fun release() { isValid = false }
}
""",
    "Texture.kt": """package android.graphics
import android.os.Handler
import android.os.Looper
class SurfaceTexture(texName: Int) {
    private var listener: ((SurfaceTexture) -> Unit)? = null
    private var handler = Handler(Looper.main)
    @Volatile private var released = false
    fun setDefaultBufferSize(w: Int, h: Int) {}
    fun setOnFrameAvailableListener(callback: ((SurfaceTexture) -> Unit)?) =
        setOnFrameAvailableListener(callback, null)
    fun setOnFrameAvailableListener(callback: ((SurfaceTexture) -> Unit)?, h: Handler?) {
        listener = callback; handler = h ?: Handler(Looper.main)
    }
    fun emit() {
        val callback = listener ?: return
        if (!released) handler.post(Runnable {
            callbackThread = Thread.currentThread().name
            callback(this)
        })
    }
    fun updateTexImage() { check(!released); updates++ }
    fun getTransformMatrix(matrix: FloatArray) {}
    fun release() { released = true }
    companion object {
        @Volatile var updates = 0
        @Volatile var callbackThread = ""
    }
}
""",
    "Gl.kt": """package android.opengl
import java.nio.FloatBuffer
class EGLSurface
object EGL14 {
    val EGL_NO_SURFACE = EGLSurface()
    const val EGL_WIDTH = 1
    const val EGL_HEIGHT = 2
    fun eglGetError() = 0
}
object GLES11Ext { const val GL_TEXTURE_EXTERNAL_OES = 1 }
object Matrix { fun setIdentityM(m: FloatArray, offset: Int) {} }
object GLES20 {
    const val GL_COLOR_BUFFER_BIT = 1
    const val GL_TEXTURE0 = 2
    const val GL_FLOAT = 3
    const val GL_TRIANGLE_STRIP = 4
    const val GL_TEXTURE_MIN_FILTER = 5
    const val GL_TEXTURE_MAG_FILTER = 6
    const val GL_LINEAR = 7
    const val GL_TEXTURE_WRAP_S = 8
    const val GL_TEXTURE_WRAP_T = 9
    const val GL_CLAMP_TO_EDGE = 10
    const val GL_VERTEX_SHADER = 11
    const val GL_FRAGMENT_SHADER = 12
    const val GL_COMPILE_STATUS = 13
    fun glViewport(x: Int, y: Int, w: Int, h: Int) {}
    fun glClear(mask: Int) {}
    fun glUseProgram(program: Int) {}
    fun glActiveTexture(texture: Int) {}
    fun glBindTexture(target: Int, texture: Int) {}
    fun glUniformMatrix4fv(loc: Int, count: Int, transpose: Boolean, matrix: FloatArray, offset: Int) {}
    fun glEnableVertexAttribArray(index: Int) {}
    fun glVertexAttribPointer(index: Int, size: Int, type: Int, normalized: Boolean, stride: Int, buffer: FloatBuffer) {}
    fun glDrawArrays(mode: Int, first: Int, count: Int) {}
    fun glDisableVertexAttribArray(index: Int) {}
    fun glGetAttribLocation(program: Int, name: String) = 1
    fun glGetUniformLocation(program: Int, name: String) = 1
    fun glGenTextures(count: Int, textures: IntArray, offset: Int) { textures[offset] = 1 }
    fun glTexParameteri(target: Int, pname: Int, param: Int) {}
    fun glCreateProgram() = 1
    fun glAttachShader(program: Int, shader: Int) {}
    fun glLinkProgram(program: Int) {}
    fun glDeleteShader(shader: Int) {}
    fun glCreateShader(type: Int) = 1
    fun glShaderSource(shader: Int, source: String) {}
    fun glCompileShader(shader: Int) {}
    fun glGetShaderiv(shader: Int, pname: Int, result: IntArray, offset: Int) { result[offset] = 1 }
    fun glGetShaderInfoLog(shader: Int) = ""
}
""",
    "Media.kt": """package android.media
import android.view.Surface
import java.nio.ByteBuffer
import java.util.concurrent.CopyOnWriteArrayList
class MediaCodecInfo(val name: String = "fake.hardware")
class MediaFormat {
    fun setInteger(key: String, value: Int) {}
    companion object {
        const val KEY_FRAME_RATE = "frame-rate"
        const val KEY_MAX_WIDTH = "max-width"
        const val KEY_MAX_HEIGHT = "max-height"
        const val KEY_MAX_INPUT_SIZE = "max-input-size"
        const val KEY_COLOR_STANDARD = "color-standard"
        const val KEY_COLOR_RANGE = "color-range"
        const val KEY_COLOR_TRANSFER = "color-transfer"
        const val KEY_ALLOW_FRAME_DROP = "allow-frame-drop"
        const val COLOR_STANDARD_BT709 = 1
        const val COLOR_RANGE_LIMITED = 2
        const val COLOR_TRANSFER_SDR_VIDEO = 3
        fun createVideoFormat(mime: String, w: Int, h: Int) = MediaFormat()
    }
}
class MediaCodec(val name: String) {
    class BufferInfo { var presentationTimeUs = 0L }
    private data class Output(val pts: Long, val readyNs: Long)
    private val pending = ArrayDeque<Output>()
    private var surface: Surface? = null
    @Volatile var stopped = false
    @Volatile var released = false
    @Volatile var outputCount = 0
    @Volatile var outputPolls = 0
    @Volatile var failNextOutput = false
    @Volatile var failStop = false
    fun configure(format: MediaFormat, target: Surface, crypto: Any?, flags: Int) { surface = target }
    fun start() {}
    fun stop() { check(!released); stopped = true; if (failStop) error("injected stop error") }
    fun release() { released = true }
    fun dequeueInputBuffer(timeoutUs: Long): Int { check(!stopped && !released); return 0 }
    fun getInputBuffer(index: Int) = ByteBuffer.allocate(128)
    fun queueInputBuffer(index: Int, offset: Int, size: Int, pts: Long, flags: Int) {
        check(!stopped && !released)
        pending.add(Output(pts, System.nanoTime() + 25_000_000L))
    }
    fun dequeueOutputBuffer(info: BufferInfo, timeoutUs: Long): Int {
        check(!stopped && !released)
        outputPolls++
        if (failNextOutput) { failNextOutput = false; error("injected decoder error") }
        val output = pending.firstOrNull() ?: return -1
        if (System.nanoTime() < output.readyNs) return -1
        info.presentationTimeUs = pending.removeFirst().pts
        return 0
    }
    fun releaseOutputBuffer(index: Int, render: Boolean) {
        check(!stopped && !released); outputCount++
        if (render) surface?.texture?.emit()
    }
    fun releaseOutputBuffer(index: Int, timestampNs: Long) = releaseOutputBuffer(index, true)
    companion object {
        val instances = CopyOnWriteArrayList<MediaCodec>()
        fun createByCodecName(name: String) = MediaCodec(name).also { instances.add(it) }
    }
}
""",
    "RendererDependencies.kt": """package io.github.jqssun.airplay.renderer
import android.content.Context
import android.media.MediaCodecInfo
import android.media.MediaFormat
import android.opengl.EGLSurface
import android.view.Surface
class Limit(val upper: Int)
class Caps { val supportedWidths = Limit(3840); val supportedHeights = Limit(2160) }
class DecoderSelector(context: Context) {
    fun avc() = MediaCodecInfo()
    fun hevc(avc: MediaCodecInfo?, w: Int, h: Int, fps: Int, force: Boolean) = MediaCodecInfo()
    fun software(mime: String, w: Int, h: Int): MediaCodecInfo? = null
    fun adaptive(info: MediaCodecInfo, mime: String) = false
    fun lowLatencyOptions(format: MediaFormat, info: MediaCodecInfo, mime: String, attempt: Int) = false
    companion object {
        const val AVC = "video/avc"
        const val HEVC = "video/hevc"
        fun MediaCodecInfo.videoCaps(mime: String) = Caps()
    }
}
class EglCore {
    init { if (failNextInit) { failNextInit = false; error("injected GL init failure") } }
    fun makeCurrent(surface: EGLSurface? = null) = true
    fun destroySurface(surface: EGLSurface) = true
    fun windowSurface(surface: Surface) = EGLSurface().also { bindings++ }
    fun query(surface: EGLSurface, what: Int) = 1920
    fun swap(surface: EGLSurface): Boolean { swaps++; return true }
    fun close() {}
    companion object {
        @Volatile var swaps = 0
        @Volatile var bindings = 0
        @Volatile var failNextInit = false
    }
}
""",
    "Regression.kt": """import android.content.Context
import android.graphics.SurfaceTexture
import android.media.MediaCodec
import android.view.Surface
import io.github.jqssun.airplay.renderer.EglCore
import io.github.jqssun.airplay.renderer.VideoRenderer

private val keyframe = byteArrayOf(0, 0, 0, 1, 0x65)
private val delta = byteArrayOf(0, 0, 0, 1, 0x41)
private fun await(description: String, condition: () -> Boolean) {
    val deadline = System.nanoTime() + 2_000_000_000L
    while (!condition()) {
        check(System.nanoTime() < deadline) { "Timed out: $description" }
        Thread.sleep(1)
    }
}
private fun workers() = Thread.getAllStackTraces().keys.filter {
    it.isAlive && it.name in setOf("VideoOutput", "VideoPipeline", "VideoFrames")
}
private fun release(renderer: VideoRenderer) {
    val tasks = List(2) { Thread { renderer.release() } }
    tasks.forEach { it.start() }
    tasks.forEach { it.join(2000); check(!it.isAlive) { "release deadlocked" } }
    check(workers().isEmpty()) { "Leaked workers: ${workers()}" }
}
private fun regression() {
    val renderer = VideoRenderer(Context())
    renderer.selectDecoders(1920, 1080, 60, false)
    renderer.scheduledOutputBufferRelease = false
    renderer.setResolution(1920, 1080)
    val firstSurface = Surface()
    renderer.setSurface(firstSurface)
    renderer.feedFrame(keyframe, 1_000_000_000L, false)
    val first = MediaCodec.instances.last()
    check(first.outputCount == 0) { "Fake must decode after feedFrame returns" }
    await("final frame drains with no next input") { first.outputCount == 1 }
    await("display callback works while main looper is never pumped") { EglCore.swaps >= 1 }
    check(SurfaceTexture.callbackThread == "VideoFrames")
    println("PASS: delayed final frame independently drains; frame callback avoids main looper")

    val codecCount = MediaCodec.instances.size
    val swapsBefore = EglCore.swaps
    val replacementSurface = Surface()
    renderer.setSurface(replacementSurface)
    renderer.clearSurface(firstSurface)
    renderer.feedFrame(delta, 1_016_666_000L, false)
    await("replacement surface still renders") { first.outputCount == 2 && EglCore.swaps > swapsBefore }
    check(MediaCodec.instances.size == codecCount) { "Surface replacement restarted codec" }
    renderer.setResolution(1280, 720)
    check(first.stopped && first.released)
    renderer.feedFrame(delta, 1_033_333_000L, false)
    check(MediaCodec.instances.size == codecCount) { "Started decoder on non-keyframe" }
    renderer.feedFrame(keyframe, 1_050_000_000L, false)
    val resized = MediaCodec.instances.last()
    await("resolution restart drains") { resized.outputCount == 1 }
    println("PASS: surface replacement preserves codec; resolution change waits for keyframe")

    renderer.stopSession()
    val idlePolls = resized.outputPolls
    await("output worker sleeps indefinitely without codec") {
        workers().single { it.name == "VideoOutput" }.state == Thread.State.WAITING
    }
    Thread.sleep(30)
    check(resized.outputPolls == idlePolls) { "Polled a stopped codec" }
    renderer.startSession()
    renderer.feedFrame(keyframe, 2_000_000_000L, false)
    val reconnected = MediaCodec.instances.last()
    await("session reconnect drains") { reconnected.outputCount == 1 }
    check(workers().count { it.name == "VideoOutput" } == 1)
    reconnected.failStop = true
    reconnected.failNextOutput = true
    await("background output failure resets codec") { reconnected.stopped && reconnected.released }
    renderer.feedFrame(keyframe, 2_016_666_000L, false)
    await("output worker recovers on next keyframe") { MediaCodec.instances.last().outputCount == 1 }
    release(renderer)
    println("PASS: stop/reconnect, background decoder error, and release worker cleanup")

    repeat(10) {
        val swaps = EglCore.swaps
        renderer.feedFrame(keyframe, 3_000_000_000L + it * 1_000_000_000L, false)
        await("renderer reuse after release") { MediaCodec.instances.last().outputCount == 1 && EglCore.swaps > swaps }
        release(renderer)
    }
    EglCore.failNextInit = true
    renderer.feedFrame(keyframe, 20_000_000_000L, false)
    renderer.feedFrame(keyframe, 20_016_666_000L, false)
    await("GL startup failure can retry") { MediaCodec.instances.last().outputCount == 1 }
    release(renderer)
    check(MediaCodec.instances.all { it.stopped && it.released })
    println("PASS: 10 full release/restarts and failed GL initialization leave no worker leaks")
}
fun main() {
    try { regression() } catch (failure: Throwable) {
        failure.printStackTrace()
        kotlin.system.exitProcess(1)
    }
}
""",
}

with tempfile.TemporaryDirectory(prefix="video-renderer-regression-") as directory:
    work = Path(directory)
    sources = []
    for filename, source in SOURCES.items():
        path = work / filename
        path.write_text(source)
        sources.append(str(path))
    renderer = arguments.renderer_dir
    sources.extend(str(renderer / name) for name in ("VideoRenderer.kt", "VideoPipeline.kt"))
    classes = work / "classes"
    subprocess.run([str(JAVA), "-cp", compiler_cp, "org.jetbrains.kotlin.cli.jvm.K2JVMCompiler",
                    "-no-stdlib", "-no-reflect", "-nowarn", "-classpath", str(stdlib),
                    "-d", str(classes), *sources], check=True, timeout=60)
    subprocess.run([str(JAVA), "-cp", os.pathsep.join(map(str, [classes, stdlib])), "RegressionKt"],
                   check=True, timeout=30)

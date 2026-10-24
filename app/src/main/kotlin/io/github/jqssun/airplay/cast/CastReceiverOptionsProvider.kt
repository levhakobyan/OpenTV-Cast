package io.github.jqssun.airplay.cast

import android.content.Context
import com.google.android.gms.cast.tv.CastReceiverOptions
import com.google.android.gms.cast.tv.ReceiverOptionsProvider

class CastReceiverOptionsProvider : ReceiverOptionsProvider {
    override fun getOptions(context: Context): CastReceiverOptions =
        CastReceiverOptions.Builder(context).build()
}

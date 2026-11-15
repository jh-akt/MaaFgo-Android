package com.maaframework.android.fgo

import com.maaframework.android.ui.MaaHostActivity

class MainActivity : MaaHostActivity() {
    override val hostVersionName: String = BuildConfig.VERSION_NAME
}

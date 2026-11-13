package com.maaframework.android.fgo

import com.maaframework.android.host.MaaHostViewModel
import android.os.Bundle
import android.view.WindowManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.maaframework.android.model.shouldKeepScreenOn
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    private val viewModel: MaaHostViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        observeKeepScreenOn()
        setContent {
            MaaFgoTheme {
                MaaFgoScreen(viewModel = viewModel)
            }
        }
    }

    private fun observeKeepScreenOn() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    val keepScreenOn = state.runtimeState.shouldKeepScreenOn()

                    if (keepScreenOn) {
                        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
                    } else {
                        window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
                    }
                }
            }
        }
    }
}

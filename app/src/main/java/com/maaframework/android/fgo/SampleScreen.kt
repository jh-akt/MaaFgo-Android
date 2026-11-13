package com.maaframework.android.fgo

import com.maaframework.android.host.MaaHostViewModel
import com.maaframework.android.host.hostActions
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.maaframework.android.host.MaaHostUiConfig
import com.maaframework.android.ui.MaaHostApp

@Composable
fun MaaFgoScreen(viewModel: MaaHostViewModel) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val actions = remember(viewModel) { viewModel.hostActions() }
    MaaHostApp(
        state = state,
        actions = actions,
        config = MaaHostUiConfig(
            appName = state.manifest.displayName,
            versionName = BuildConfig.VERSION_NAME,
        ),
    )
}

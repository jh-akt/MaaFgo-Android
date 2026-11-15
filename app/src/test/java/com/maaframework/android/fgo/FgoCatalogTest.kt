package com.maaframework.android.fgo

import com.maaframework.android.catalog.InterfaceCatalogLoader
import com.maaframework.android.catalog.TaskOptionSupport
import com.maaframework.android.host.MaaHostViewModel
import com.maaframework.android.project.MaaProjectManifest
import com.maaframework.android.runtime.ProjectLocalOverlay
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.io.File
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test

class FgoCatalogTest {
    private val assets = File(requireNotNull(System.getProperty("fgo.assets")))
    private val manifest = Json.decodeFromString<MaaProjectManifest>(File(assets, "maa_project_manifest.json").readText())
    private val catalog = InterfaceCatalogLoader(supportedControllers = manifest.supportedControllers)
        .loadFromDirectory(File(assets, "project"))

    @Test fun `Android resources expose both servers and default only to login`() {
        assertEquals(26, catalog.tasks.size)
        assertEquals(setOf("B服(小米/应用宝服)", "日服"), catalog.resources.map { it.id }.toSet())
        assertTrue(catalog.tasks.none { it.id in setOf("启动bbc", "关闭bbc", "__MXU_KILLPROC__") })
        assertEquals(setOf("登录"), MaaHostViewModel.defaultCheckedTaskIds(catalog.tasks, manifest.defaultTaskId))
        assertEquals("project", manifest.bundledResourcePath)
        assertEquals(240, manifest.virtualDisplayDpi)
        assertEquals("com.bilibili.fatego/.UnityPlayerNativeActivity", manifest.packageNameFor(manifest.defaultResourceId))
        assertEquals("com.aniplex.fategrandorder", manifest.packageNameFor("日服"))
    }

    @Test fun `bundled payload and online updater share the local overlay`() {
        val overlay = ProjectLocalOverlay { File(assets, "${manifest.localOverlayPath}/$it").readBytes() }
        val marker = Json.parseToJsonElement(File(assets, "project/.maafgo-generated.json").readText()).jsonObject
        assertEquals(marker.getValue("overlay_sha256").jsonPrimitive.content, overlay.fingerprint())
        assertEquals(marker.getValue("tag").jsonPrimitive.content, manifest.githubRelease!!.bundledVersion)
        assertTrue(File(assets, "project/agent/battle/runtime/runtime.py").readText().contains("default_target=1,"))
        assertTrue(manifest.hasResourceUpdateSource())
    }

    @Test fun `server options and translated presets survive host parsing`() {
        val cn = catalog.resources.first { it.id == manifest.defaultResourceId }
        val jp = catalog.resources.first { it.id == "日服" }
        assertEquals(setOf("cn"), TaskOptionSupport.defaultSelectionForOption(cn.options.single()))
        assertEquals(setOf("jp"), TaskOptionSupport.defaultSelectionForOption(jp.options.single()))
        assertTrue(catalog.tasks.first { it.id == "登录" }.options.isNotEmpty())
        assertTrue(catalog.tasks.first { it.id == "日常战斗" }.options.isNotEmpty())
        assertTrue(catalog.presets.none { it.label.startsWith("$") })
        assertFalse(catalog.presets.first { it.id == "daily_event" }.taskIds.contains("小活动"))
        assertTrue(catalog.presets.first { it.id == "story" }.taskIds.isEmpty())
        assertTrue(catalog.presets.first { it.id == "daily_training" }.taskIds.isEmpty())
    }
}

package org.faran.university;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.print.PrintManager;
import android.util.Base64;
import androidx.activity.result.ActivityResult;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.ActivityCallback;
import com.getcapacitor.annotation.CapacitorPlugin;
import java.io.IOException;
import java.io.OutputStream;

@CapacitorPlugin(name = "StudyDocuments")
public class StudyDocuments extends Plugin {
    @PluginMethod
    public void save(PluginCall call) {
        String name = call.getString("name", "");
        String type = call.getString("type", "");
        String data = call.getString("data", "");
        if (!name.matches("[a-zA-Z0-9._-]{1,96}") || data.isEmpty() || data.length() > 16000000
            || !((type.equals("application/pdf") && name.endsWith(".pdf"))
                || (type.equals("text/csv") && name.endsWith(".csv"))
                || (type.equals("application/json") && name.endsWith(".json")))) {
            call.reject("Unsupported document");
            return;
        }
        Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT)
            .addCategory(Intent.CATEGORY_OPENABLE)
            .setType(type)
            .putExtra(Intent.EXTRA_TITLE, name);
        startActivityForResult(call, intent, "writeDocument");
    }

    @ActivityCallback
    private void writeDocument(PluginCall call, ActivityResult result) {
        if (call == null) return;
        Intent intent = result.getData();
        Uri target = intent == null ? null : intent.getData();
        if (result.getResultCode() != Activity.RESULT_OK || target == null) {
            call.resolve(new JSObject().put("saved", false));
            return;
        }
        execute(() -> {
            try (OutputStream stream = getContext().getContentResolver().openOutputStream(target, "w")) {
                if (stream == null) throw new IOException("No output stream");
                stream.write(Base64.decode(call.getString("data", ""), Base64.DEFAULT));
                call.resolve(new JSObject().put("saved", true));
            } catch (IOException | IllegalArgumentException | SecurityException failure) {
                call.reject("Could not save the document", failure);
            }
        });
    }

    @PluginMethod
    public void printPage(PluginCall call) {
        getActivity().runOnUiThread(() -> {
            PrintManager manager = (PrintManager) getContext().getSystemService(Context.PRINT_SERVICE);
            if (manager == null) {
                call.reject("Printing unavailable");
                return;
            }
            String title = getContext().getString(R.string.app_name);
            manager.print(title, getBridge().getWebView().createPrintDocumentAdapter(title), null);
            call.resolve();
        });
    }
}

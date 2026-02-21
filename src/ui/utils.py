import threading
import urllib.request
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GLib

IMG_CACHE = {}


class AsyncImage(Gtk.Image):
    def __init__(
        self, url=None, size=None, width=None, height=None, circular=False, **kwargs
    ):
        super().__init__(**kwargs)

        # Determine target dimensions
        self.target_w = width if width else size
        self.target_h = height if height else size

        if not self.target_w:
            self.target_w = 48
        if not self.target_h:
            self.target_h = 48

        # Set pixel size if provided (limits size for icons).
        if size:
            self.set_pixel_size(size)
        else:
            # Rely on pixbuf scaling for explicit width/height.
            pass

        self.set_from_icon_name("image-missing-symbolic")  # Placeholder
        self.url = url
        self.circular = circular

        if url:
            self.load_url(url)

    # ... (load_url, _fetch_image same) ...

    def load_url(self, url):
        self.url = url
        if not url:
            self.set_from_icon_name("image-missing-symbolic")
            return

        # Check Cache
        if url in IMG_CACHE:
            # Found in cache, use it immediately
            pixbuf = IMG_CACHE[url]
            self._apply_pixbuf(pixbuf)
            return

        thread = threading.Thread(target=self._fetch_image, args=(url,))
        thread.daemon = True
        thread.start()

    def _fetch_image(self, url):
        try:
            # Download image data
            with urllib.request.urlopen(url) as response:
                data = response.read()

            loader = GdkPixbuf.PixbufLoader()
            loader.write(data)
            loader.close()
            pixbuf = loader.get_pixbuf()

            if pixbuf:
                # Cache the original full-res pixbuf
                IMG_CACHE[url] = pixbuf

                # Apply (will scale if needed)
                GLib.idle_add(self._apply_pixbuf, pixbuf)

        except Exception as e:
            print(f"Failed to load image {url}: {e}")

    def _apply_pixbuf(self, pixbuf):
        w = pixbuf.get_width()
        h = pixbuf.get_height()

        tw = self.target_w
        th = self.target_h

        # Calculate scale to fill the target size (cover)
        scale = max(tw / w, th / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        # Scale properly
        scaled = pixbuf.scale_simple(new_w, new_h, GdkPixbuf.InterpType.BILINEAR)

        # Verify valid scaling
        if not scaled:
            scaled = pixbuf

        # Center crop to target dimensions
        final_pixbuf = scaled
        if new_w > tw or new_h > th:
            offset_x = max(0, (new_w - tw) // 2)
            offset_y = max(0, (new_h - th) // 2)

            # Calculate width/height to crop
            # Ensure we don't request more than available from offset
            cw = min(tw, new_w - offset_x)
            ch = min(th, new_h - offset_y)

            # Sanity check prevents empty or negative dimensions
            if cw > 0 and ch > 0:
                try:
                    final_pixbuf = subprocess_pixbuf(scaled, offset_x, offset_y, cw, ch)
                except Exception as e:
                    print(f"Pixbuf crop error: {e}")
                    final_pixbuf = scaled
            else:
                final_pixbuf = scaled

        if self.circular:
            # Use CSS for circular styling.
            self.add_css_class("circular")

        self.set_from_pixbuf(final_pixbuf)


def subprocess_pixbuf(pixbuf, x, y, w, h):
    # bindings helper
    return pixbuf.new_subpixbuf(x, y, w, h)


class AsyncPicture(Gtk.Picture):
    # Added crop_to_square parameter
    def __init__(self, url=None, crop_to_square=False, **kwargs):
        super().__init__(**kwargs)
        self.set_content_fit(Gtk.ContentFit.COVER)
        self.crop_to_square = crop_to_square
        self.url = url
        if url:
            self.load_url(url)

    def load_url(self, url):
        self.url = url
        if not url:
            self.set_paintable(None)
            return

        if url in IMG_CACHE:
            self._apply_pixbuf(IMG_CACHE[url])
            return

        thread = threading.Thread(target=self._fetch_image, args=(url,))
        thread.daemon = True
        thread.start()

    def _fetch_image(self, url):
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()

            loader = GdkPixbuf.PixbufLoader()
            loader.write(data)
            loader.close()
            pixbuf = loader.get_pixbuf()

            if pixbuf:
                IMG_CACHE[url] = pixbuf
                GLib.idle_add(self._apply_pixbuf, pixbuf)

        except Exception as e:
            print(f"AsyncPicture error {url}: {e}")

    def _apply_pixbuf(self, pixbuf):
        # MAGIC HAPPENS HERE: Force center-crop to a 1:1 square
        if self.crop_to_square:
            w = pixbuf.get_width()
            h = pixbuf.get_height()
            if w != h:
                # Find the smallest dimension
                size = min(w, h)
                # Calculate offsets to crop evenly from both sides
                offset_x = (w - size) // 2
                offset_y = (h - size) // 2
                # Create a perfectly square sub-image
                pixbuf = pixbuf.new_subpixbuf(offset_x, offset_y, size, size)

        # Convert to Texture and paint
        texture = Gdk.Texture.new_for_pixbuf(pixbuf)
        self.set_paintable(texture)


class MarqueeLabel(Gtk.ScrolledWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # EXTERNAL means the content can overflow, but no scrollbars are drawn
        self.set_policy(Gtk.PolicyType.EXTERNAL, Gtk.PolicyType.NEVER)

        self.label = Gtk.Label()
        self.label.set_halign(Gtk.Align.START)
        self.label.set_valign(Gtk.Align.CENTER)
        self.set_child(self.label)

        # Animation variables
        self._tick_id = 0
        self._pause_frames = 60  # Pause for ~1 second at the edges
        self._current_pause = self._pause_frames
        self._direction = 1  # 1 = scrolling right, -1 = scrolling left

        # Only animate when actually visible on screen
        self.connect("map", self._start_marquee)
        self.connect("unmap", self._stop_marquee)

    def set_label(self, text):
        self.label.set_label(text)
        # Reset position and animation state when text changes
        self.get_hadjustment().set_value(0)
        self._current_pause = self._pause_frames
        self._direction = 1

    def add_css_class(self, class_name):
        # Apply CSS to the actual text label, not the scrolled window container
        self.label.add_css_class(class_name)

    def _start_marquee(self, *args):
        if self._tick_id == 0:
            # Sync to the monitor's frame clock for buttery smooth movement
            self._tick_id = self.add_tick_callback(self._on_tick)

    def _stop_marquee(self, *args):
        if self._tick_id != 0:
            self.remove_tick_callback(self._tick_id)
            self._tick_id = 0

    def _on_tick(self, widget, frame_clock):
        adj = self.get_hadjustment()
        max_val = adj.get_upper() - adj.get_page_size()

        # If the text fits perfectly, don't scroll at all!
        if max_val <= 0:
            adj.set_value(0)
            return True

        # Handle the pause at the edges
        if self._current_pause > 0:
            self._current_pause -= 1
            return True

        # Move the text by 1 pixel per frame
        new_val = adj.get_value() + (1.0 * self._direction)

        # Reverse direction if we hit an edge
        if new_val >= max_val:
            new_val = max_val
            self._direction = -1
            self._current_pause = self._pause_frames
        elif new_val <= 0:
            new_val = 0
            self._direction = 1
            self._current_pause = self._pause_frames

        adj.set_value(new_val)
        return True


class LikeButton(Gtk.Button):
    def __init__(self, client, video_id, initial_status="INDIFFERENT", **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.video_id = video_id
        self.status = initial_status

        self.add_css_class("flat")
        self.add_css_class("circular")
        self.set_valign(Gtk.Align.CENTER)

        self.update_icon()
        self.connect("clicked", self.on_clicked)

    def update_icon(self):
        if self.status == "LIKE":
            self.set_icon_name("starred-symbolic")
            self.add_css_class("liked-button")  # For potential CSS styling
            self.set_tooltip_text("Unlike")
        elif self.status == "DISLIKE":
            self.set_icon_name(
                "view-restore-symbolic"
            )  # Placeholder or specific icon if found
            self.set_tooltip_text("Disliked")
        else:
            self.set_icon_name("non-starred-symbolic")
            self.remove_css_class("liked-button")
            self.set_tooltip_text("Like")

    def on_clicked(self, btn):
        # Toggle: LIKE -> INDIFFERENT, others -> LIKE
        new_status = "INDIFFERENT" if self.status == "LIKE" else "LIKE"

        # Optimistic update
        old_status = self.status
        self.status = new_status
        self.update_icon()

        def do_rate():
            success = self.client.rate_song(self.video_id, new_status)
            if not success:
                # Revert on failure
                GLib.idle_add(self.revert, old_status)

        thread = threading.Thread(target=do_rate)
        thread.daemon = True
        thread.start()

    def revert(self, status):
        self.status = status
        self.update_icon()

    def set_data(self, video_id, status):
        self.video_id = video_id
        self.status = status
        self.update_icon()
        self.set_visible(bool(video_id))

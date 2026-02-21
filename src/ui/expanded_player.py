import gi
from gi.repository import Gtk, Adw, GObject, Pango
from ui.utils import AsyncPicture, LikeButton, MarqueeLabel
from ui.queue_panel import QueuePanel


class ExpandedPlayer(Gtk.Box):
    @GObject.Signal
    def dismiss(self):
        pass

    def __init__(self, player, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        self.player = player
        self.player_state = "stopped"

        # 1. The Stack: Transitions between Player and Queue
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_vexpand(True)
        self.append(self.stack)

        # ==========================================
        # PAGE 1: THE PLAYER VIEW
        # ==========================================
        self.player_scroll = Gtk.ScrolledWindow()
        self.player_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.player_scroll.set_propagate_natural_height(True)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(32)
        main_box.set_margin_end(32)

        # Header with Dismiss Button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header_box.set_margin_top(8)
        header_box.set_margin_bottom(16)

        dismiss_btn = Gtk.Button(icon_name="go-down-symbolic")
        dismiss_btn.add_css_class("flat")
        dismiss_btn.add_css_class("circular")
        dismiss_btn.connect("clicked", lambda x: self.emit("dismiss"))
        header_box.append(dismiss_btn)

        header_spacer = Gtk.Box()
        header_spacer.set_hexpand(True)
        header_box.append(header_spacer)
        main_box.append(header_box)

        # Cover Art
        self.cover_img = AsyncPicture(crop_to_square=True)
        self.cover_img.add_css_class("rounded")
        self.cover_img.set_halign(Gtk.Align.FILL)
        self.cover_img.set_valign(Gtk.Align.FILL)

        cover_frame = Gtk.AspectFrame(ratio=1.0, obey_child=False)
        cover_frame.set_halign(Gtk.Align.CENTER)
        cover_frame.set_valign(Gtk.Align.CENTER)
        cover_frame.set_vexpand(True)
        cover_frame.set_hexpand(True)
        cover_frame.set_child(self.cover_img)
        main_box.append(cover_frame)

        # Metadata & Like
        meta_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        meta_row.set_halign(Gtk.Align.FILL)

        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        text_box.set_hexpand(True)
        text_box.set_valign(Gtk.Align.CENTER)

        # --- Marquee Title ---
        self.title_label = MarqueeLabel()
        self.title_label.set_label("Not Playing")
        self.title_label.add_css_class("title-1")

        self.artist_label = Gtk.Label(label="")
        self.artist_label.add_css_class("heading")
        self.artist_label.set_opacity(0.7)
        self.artist_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.artist_label.set_halign(Gtk.Align.START)

        text_box.append(self.title_label)
        text_box.append(self.artist_label)

        self.like_btn = LikeButton(self.player.client, None)
        self.like_btn.set_visible(False)
        self.like_btn.set_valign(Gtk.Align.CENTER)

        meta_row.append(text_box)
        meta_row.append(self.like_btn)
        main_box.append(meta_row)

        # Progress Slider
        progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self.scale.set_range(0, 100)
        self.scale.connect("change-value", self.on_scale_change_value)
        progress_box.append(self.scale)

        timings_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.pos_label = Gtk.Label(label="0:00")
        self.pos_label.add_css_class("caption")
        self.pos_label.add_css_class("numeric")

        dur_spacer = Gtk.Box()
        dur_spacer.set_hexpand(True)

        self.dur_label = Gtk.Label(label="0:00")
        self.dur_label.add_css_class("caption")
        self.dur_label.add_css_class("numeric")

        timings_box.append(self.pos_label)
        timings_box.append(dur_spacer)
        timings_box.append(self.dur_label)
        progress_box.append(timings_box)
        main_box.append(progress_box)

        # Media Controls
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        controls_box.set_halign(Gtk.Align.CENTER)
        controls_box.set_margin_top(8)

        self.prev_btn = Gtk.Button(icon_name="media-skip-backward-symbolic")
        self.prev_btn.set_size_request(56, 56)
        self.prev_btn.add_css_class("circular")
        self.prev_btn.set_valign(Gtk.Align.CENTER)
        self.prev_btn.connect("clicked", lambda x: self.player.previous())

        self.play_btn = Gtk.Button()
        self.play_btn.set_size_request(80, 80)
        self.play_btn.add_css_class("circular")
        self.play_btn.add_css_class("suggested-action")
        self.play_btn.set_valign(Gtk.Align.CENTER)
        self.play_btn.connect("clicked", self.on_play_clicked)

        self.play_icon = Gtk.Image.new_from_icon_name("media-playback-start-symbolic")
        self.play_icon.set_pixel_size(32)
        self.play_btn.set_child(self.play_icon)

        self.next_btn = Gtk.Button(icon_name="media-skip-forward-symbolic")
        self.next_btn.set_size_request(56, 56)
        self.next_btn.add_css_class("circular")
        self.next_btn.set_valign(Gtk.Align.CENTER)
        self.next_btn.connect("clicked", lambda x: self.player.next())

        controls_box.append(self.prev_btn)
        controls_box.append(self.play_btn)
        controls_box.append(self.next_btn)
        main_box.append(controls_box)

        # Bottom Row: Volume & Queue Toggle
        bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        bottom_box.set_halign(Gtk.Align.FILL)
        bottom_box.set_margin_top(24)

        vol_icon = Gtk.Image.new_from_icon_name("audio-volume-high-symbolic")
        vol_icon.set_opacity(0.7)

        self.volume_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self.volume_scale.set_range(0, 1.0)
        self.volume_scale.set_hexpand(True)
        self.volume_scale.set_value(self.player.get_volume())
        self.volume_scale.connect("value-changed", self.on_volume_scale_changed)

        self.show_queue_btn = Gtk.Button(icon_name="view-list-symbolic")
        self.show_queue_btn.add_css_class("flat")
        self.show_queue_btn.add_css_class("circular")
        self.show_queue_btn.connect(
            "clicked", lambda x: self.stack.set_visible_child_name("queue")
        )

        bottom_box.append(vol_icon)
        bottom_box.append(self.volume_scale)
        bottom_box.append(self.show_queue_btn)
        main_box.append(bottom_box)

        self.player_scroll.set_child(main_box)
        self.stack.add_named(self.player_scroll, "player")

        # ==========================================
        # PAGE 2: THE QUEUE VIEW
        # ==========================================
        queue_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        queue_box.set_margin_top(12)

        q_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        q_header.set_margin_start(16)
        q_header.set_margin_end(16)
        q_header.set_margin_bottom(12)

        back_btn = Gtk.Button(icon_name="go-previous-symbolic")
        back_btn.add_css_class("flat")
        back_btn.add_css_class("circular")
        back_btn.connect(
            "clicked", lambda x: self.stack.set_visible_child_name("player")
        )

        q_title = Gtk.Label(label="")
        q_title.add_css_class("heading")
        q_title.set_hexpand(True)
        q_title.set_halign(Gtk.Align.CENTER)

        q_spacer = Gtk.Box()
        q_spacer.set_size_request(32, -1)

        q_header.append(back_btn)
        q_header.append(q_title)
        q_header.append(q_spacer)
        queue_box.append(q_header)

        self.queue_panel = QueuePanel(self.player)
        self.queue_panel.set_vexpand(True)
        queue_box.append(self.queue_panel)

        self.stack.add_named(queue_box, "queue")

        # Connect Signals
        self.player.connect("metadata-changed", self.on_metadata_changed)
        self.player.connect("progression", self.on_progression)
        self.player.connect("state-changed", self.on_state_changed)
        self.player.connect("volume-changed", self.on_volume_changed)

    # --- SIGNAL HANDLERS ---
    def on_metadata_changed(
        self, player, title, artist, thumbnail_url, video_id, like_status
    ):
        self.title_label.set_label(title)  # Now updates MarqueeLabel
        self.artist_label.set_label(artist)
        if thumbnail_url:
            thumbnail_url = thumbnail_url.replace("w120-h120", "w640-h640").replace(
                "sddefault", "maxresdefault"
            )
            self.cover_img.load_url(thumbnail_url)
        else:
            self.cover_img.load_url(None)

        if video_id:
            self.like_btn.set_data(video_id, like_status)
            self.like_btn.set_visible(True)
        else:
            self.like_btn.set_visible(False)

    def on_progression(self, player, pos, dur):
        self.scale.set_range(0, dur)
        self.scale.set_value(pos)
        self.pos_label.set_label(self._format_time(pos))
        self.dur_label.set_label(self._format_time(dur))

    def _format_time(self, seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m}:{s:02d}"

    def on_scale_change_value(self, scale, scroll, value):
        self.player.seek(value)
        return False

    def on_play_clicked(self, btn):
        if self.player_state == "playing":
            self.player.pause()
        else:
            self.player.play()

    def on_state_changed(self, player, state):
        self.player_state = state
        icon = (
            "media-playback-pause-symbolic"
            if state == "playing"
            else "media-playback-start-symbolic"
        )
        self.play_icon.set_from_icon_name(icon)

    def on_volume_scale_changed(self, scale):
        self.player.set_volume(scale.get_value())

    def on_volume_changed(self, player, volume, muted):
        if abs(self.volume_scale.get_value() - volume) > 0.01:
            self.volume_scale.set_value(volume)

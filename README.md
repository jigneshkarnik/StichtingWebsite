# Sanskriti & Sanskar Website

Official website for the Sanskriti & Sanskar Foundation - celebrating Indian culture and heritage in the Netherlands.

## 🌟 Features

- **Event Gallery**: Browse our collection of cultural events with photos and videos
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Cloudinary Integration**: Optimized image delivery and management
- **Automated Event Addition**: Streamlined process for adding new events

## 🚀 Quick Links

- 🌐 [Live Website](https://www.sanskriti-en-sanskar.nl/) (if applicable)
- 📸 [Event Gallery](events.html)
- 📝 [Add New Event](docs/ADD_NEW_EVENT.md)
- 🐛 [Report Issues](../../issues)

## 📚 Adding New Events

We've automated the process of adding events to make it quick and easy!

### Quick Start (5 minutes)

1. **Upload photos** to Cloudinary
2. **Create an issue** using our [Add New Event template](../../issues/new?template=add-event.yml)
3. **Add the `new-event` label** to trigger automation
4. **Review and merge** the automatically created Pull Request

That's it! The automation handles:
- ✅ Fetching photos from Cloudinary
- ✅ Updating event mappings
- ✅ Generating gallery entries
- ✅ Creating a ready-to-merge PR

👉 **[Full Documentation](docs/ADD_NEW_EVENT.md)** for detailed instructions and troubleshooting

## 🛠️ Development

### Project Structure

```
.
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── add-event.yml          # Template for adding events
│   └── workflows/
│       └── add-event.yml           # Automation workflow
├── docs/
│   └── ADD_NEW_EVENT.md           # Event addition documentation
├── scripts/
│   └── add_event_from_issue.py   # Event automation script
├── cloudinary_event_mapping.json  # Event data storage
├── gallery.js                     # Gallery functionality
├── gallery.css                    # Gallery styles
├── events.html                    # Events listing page
├── gallery.html                   # Photo gallery viewer
└── update_website.py              # Website generator script
```

### Technologies Used

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Image Management**: Cloudinary
- **Automation**: GitHub Actions, Python 3.10
- **Version Control**: Git & GitHub

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/jigneshkarnik/StichtingWebsite.git
   cd StichtingWebsite
   ```

2. Open `index.html` in your browser to view the website locally

3. For event management:
   ```bash
   pip install cloudinary
   python update_website.py
   ```

## 🔐 Security

- API keys are stored securely in GitHub Secrets
- No credentials are committed to the repository
- All external resources use HTTPS

### Required Secrets (for automation)

- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

## 📖 Documentation

- [Adding New Events](docs/ADD_NEW_EVENT.md) - Complete guide for adding events
- [GitHub Workflow](.github/workflows/add-event.yml) - Automation configuration
- [Issue Template](.github/ISSUE_TEMPLATE/add-event.yml) - Event submission form

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report bugs** by opening an [issue](../../issues)
2. **Suggest features** using the feature request template
3. **Submit pull requests** with improvements
4. **Add events** using our automated process

### Contribution Guidelines

- Keep changes focused and minimal
- Test locally before submitting PRs
- Follow existing code style
- Update documentation if needed

## 📝 License

This project is maintained by the Sanskriti & Sanskar Foundation.

## 👥 Maintainers

- [@jigneshkarnik](https://github.com/jigneshkarnik)

## 📞 Contact

For questions or support:
- Open an [issue](../../issues)
- Visit our [website](https://www.sanskriti-en-sanskar.nl/) (if applicable)

---

**Made with ❤️ for the Indian community in the Netherlands**

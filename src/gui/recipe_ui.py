import customtkinter as ctk
import logging
from scripts.recipe_script import RecipeScript

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

class RecipeUI:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.script = RecipeScript()

        self.default_font = ctk.CTkFont(family="Helvetica", size=16)
        self.title_font = ctk.CTkFont(
            family=self.default_font.cget("family"),
            size=self.default_font.cget("size") + 4,
            weight="bold",
        )

        self.setup_ui()

    def setup_ui(self):
        """Sets up the UI components for the Recipe script."""
        # Dashboard Frame
        self.recipe_dashboard_frame = ctk.CTkFrame(
            self.parent_frame, corner_radius=10, border_width=2
        )
        self.recipe_dashboard_frame.pack(fill="both", expand=True, pady=10, padx=10)

        # self.recipe_dashboard_frame.grid_columnconfigure(0, weight=1)
        # self.recipe_dashboard_frame.grid_columnconfigure(1, weight=4)
        # self.recipe_dashboard_frame.grid_rowconfigure(0, weight=1)
        # self.recipe_dashboard_frame.grid_rowconfigure(1, weight=8)

        # Title label
        self.dashboard_title_label = ctk.CTkLabel(
            self.recipe_dashboard_frame, text="Recipe Finder", font=self.title_font
        )
        self.dashboard_title_label.pack(pady=10)

        # Ingredients Input
        self.ingredients_frame = ctk.CTkFrame(self.recipe_dashboard_frame)
        self.ingredients_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.ingredients_label = ctk.CTkLabel(
            self.ingredients_frame,
            text="Enter Ingredients (comma-separated):",
            font=self.default_font,
        )
        self.ingredients_label.pack(padx=10, pady=5)

        self.ingredients_entry = ctk.CTkEntry(
            self.ingredients_frame, width=200, font=self.default_font
        )
        self.ingredients_entry.pack(padx=10, pady=5)

        self.num_of_ingredients_label = ctk.CTkLabel(
            self.ingredients_frame,
            text="Number of Recipes to Fetch:",
            font=self.default_font,
        )
        self.num_of_ingredients_label.pack(padx=10, pady=5)

        self.num_of_ingredients_entry = ctk.CTkEntry(
            self.ingredients_frame, width=200, font=self.default_font
        )
        self.num_of_ingredients_entry.pack(padx=10, pady=5)

        self.get_recipe_button = ctk.CTkButton(
            self.ingredients_frame,
            text="Get Recipes",
            font=self.default_font,
            command=self.get_and_display_recipes,
        )
        self.get_recipe_button.pack(padx=10, pady=5)

        # Recipe Display
        self.recipe_display_frame = ctk.CTkScrollableFrame(self.recipe_dashboard_frame, corner_radius=10)
        self.recipe_display_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.recipe_title_label = ctk.CTkLabel(
            self.recipe_display_frame, text="Recipe Results", font=self.title_font
        )
        self.recipe_title_label.pack(pady=10)

        self.recipe_info_label = ctk.CTkLabel(
            self.recipe_display_frame, text="Recipe Information", font=self.default_font
        )
        self.recipe_info_label.pack(pady=10)

    def get_and_display_recipes(self):
        """Fetches recipes based on user input and updates the UI."""
        ingredients = self.ingredients_entry.get()
        num_of_recipes = self.num_of_ingredients_entry.get()
        recipes = self.script.get_recipes(ingredients, number=num_of_recipes)
        logging.debug(f"Fetched recipes: {recipes}")

        if recipes:
            self.display_recipes(recipes)
            recipe_names = [recipe['title'] for recipe in recipes]
            logging.info(f"Displayed recipes: {recipe_names}")
        else:
            self.recipe_info_label.configure(text="No recipes found.")
            logging.info("No recipes found to display.")

    def display_recipes(self, recipes):
        """Updates the UI with the fetched recipes."""
        for widget in self.recipe_display_frame.winfo_children():
            widget.destroy()
            
        if "error" in recipes:
            logging.debug(f"Error fetching recipes: {recipes['error']}")
            self.recipe_info_label.configure(
                text=f"Error fetching data: {recipes['error']}"
            )
        else:
            if recipes:
                for recipe in recipes:
                    # Create recipe frame
                    recipe_frame = ctk.CTkFrame(self.recipe_display_frame, corner_radius=5)
                    recipe_frame.pack(fill="x", padx=5, pady=5)

                    recipe_title = ctk.CTkLabel(
                        recipe_frame, text=recipe['title'], font=self.title_font
                    )
                    recipe_title.pack(side="top", padx=5, pady=2)

                    # Get and display recipe image
                    recipe_image = self.script.get_recipe_image(recipe.get('image'))
                    if recipe_image:
                        image = ctk.CTkImage(recipe_image, size=(200, 200))
                        recipe_image = ctk.CTkLabel(
                            recipe_frame, image=image, text="", font=self.default_font
                        )
                        recipe_image.pack(side="top", padx=5, pady=2)

                    # Ingredients info
                    used_ingredients = ", ".join(ing['name'] for ing in recipe['usedIngredients'])
                    missing_ingredients = ", ".join(ing['name'] for ing in recipe['missedIngredients'])
                    unused_ingredients = ", ".join(ing['name'] for ing in recipe.get('unusedIngredients', []))

                    ingredients_info = ctk.CTkLabel(
                        recipe_frame, text=f"Used: {used_ingredients}\nMissing: {missing_ingredients}\nUnused: {unused_ingredients}", font=self.default_font
                    )
                    ingredients_info.pack(side="top", padx=5, pady=2)

                    # Instructions
                    instructions_info = ", \n".join(ing['original'] for ing in recipe['usedIngredients'] + recipe['missedIngredients'])

                    instructions_title = ctk.CTkLabel(
                        recipe_frame, text="Instructions:", font=self.title_font
                    )
                    instructions_title.pack(side="top", padx=5, pady=2)

                    instructions_label = ctk.CTkLabel(
                        recipe_frame, text=instructions_info, font=self.default_font, wraplength=400, justify="left"
                    )
                    instructions_label.pack(side="top", padx=5, pady=2)

            else:
                self.recipe_info_label.configure(text="No recipes found.")
                logging.info("No recipes found to display.")

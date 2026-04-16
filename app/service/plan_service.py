import pandas as pd
import io
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError


class PlanService:
    def __init__(self, plan_repo):
        self.plan_repo = plan_repo

    def import_plans_from_excel(self, file: UploadFile):
        try:
            contents = file.file.read()
            df = pd.read_excel(io.BytesIO(contents))
        except FileNotFoundError:
            raise HTTPException(status_code=400, detail="Not correct file Excel")
        finally:
            file.file.close()

        required_columns = {'period', 'category_name', 'sum'}
        if not required_columns.issubset(df.columns):
            raise HTTPException(status_code=400, detail="Missing required columns")

        try:
            for index, row in df.iterrows():
                period_raw = row['period']
                cat_name = str(row['category_name']).strip()
                amount = row['sum']

                if pd.isna(amount):
                    raise ValueError(f"Row {index + 2}: Sum dose not be NaN")

                if isinstance(period_raw, datetime):
                    period_date = period_raw.date()
                else:
                    try:
                        period_date = datetime.strptime(str(period_raw), "%d.%m.%Y").date()
                    except ValueError:
                        raise ValueError(f"Row {index + 2}: Not a correct date format YYYY-MM-DD")

                if period_date.day != 1:
                    raise ValueError(f"Row {index + 2}: Date must be begin of first day month")

                category = self.plan_repo.get_category_by_name(cat_name)
                if not category:
                    raise ValueError(f"Row {index+2}: Category '{cat_name}' not found")

                existing_plan = self.plan_repo.check_plan_exists(category.id, period_date)
                if existing_plan:
                    raise ValueError(
                        f"Plan for '{cat_name}' on period {period_date.strftime('%m.%Y')} already exists"
                    )

                self.plan_repo.create_plan(
                    period=period_date,
                    amount=Decimal(str(amount)),
                    category_id=category.id
                )

            self.plan_repo.commit()
            return {"status": "success", "message": f"Installed successfully {len(df)} entries"}

        except ValueError as ve:
            self.plan_repo.rollback()
            raise HTTPException(status_code=400, detail=str(ve))
        except SQLAlchemyError as se:
            self.plan_repo.rollback()
            raise HTTPException(status_code=500, detail="Database error while saving")
        except Exception as e:
            self.plan_repo.rollback()
            raise HTTPException(status_code=500, detail=f"An unexpected error: {str(e)}")


